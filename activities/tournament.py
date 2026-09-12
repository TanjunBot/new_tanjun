from __future__ import annotations

import asyncio
import logging
import math
import random
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from activities.base import BaseGame, Player

logger = logging.getLogger(__name__)


class TournamentRewards(BaseModel):
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    xp_1st: int = 0
    xp_2nd: int = 0
    xp_3rd: int = 0
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    can_grant_xp: bool = False
    can_grant_role: bool = False
    rewards_granted: bool = False


class TournamentPlayer(BaseModel):
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    score: int = 0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    is_eliminated: bool = False
    is_host: bool = False
    connected: bool = True


class TournamentMatch:
    def __init__(
        self,
        match_id: str,
        round_index: int,
        game_type: str,
        player1: TournamentPlayer,
        player2: Optional[TournamentPlayer],  # None = Bye
        game_instance: Optional[BaseGame] = None
    ) -> None:
        self.match_id: str = match_id
        self.round_index: int = round_index
        self.game_type: str = game_type
        self.player1: TournamentPlayer = player1
        self.player2: Optional[TournamentPlayer] = player2
        self.game_instance: Optional[BaseGame] = game_instance
        self.status: str = "pending"  # "pending", "active", "finished"
        self.winner_id: Optional[str] = None  # user_id, "draw", or "bye"
        self.is_bye: bool = (player2 is None)
        self.cheers: List[Dict[str, str]] = []

    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        game_state = self.game_instance.get_state(for_user_id=for_user_id) if self.game_instance else None
        return {
            "match_id": self.match_id,
            "round_index": self.round_index,
            "game_type": self.game_type,
            "player1": self.player1.model_dump(),
            "player2": self.player2.model_dump() if self.player2 else None,
            "status": self.status,
            "winner_id": self.winner_id,
            "is_bye": self.is_bye,
            "cheers": self.cheers[-8:],
            "game_state": game_state
        }


class Tournament:
    """Manages multi-game Tanjun Cup tournaments with flexible game selection per round, points accumulation, and podium celebration."""

    def __init__(self, session_id: str, host: Player) -> None:
        self.session_id: str = session_id
        self.host_id: str = host.user_id
        self.title: str = "Tanjun Cup"
        self.status: str = "lobby"  # "lobby", "active", "round_end", "finished"
        self.format: str = "points"  # "points" (Mehrkampf) or "knockout"
        self.match_style: str = "spectated"  # "spectated" (Live Showmatch) or "parallel"
        self.total_rounds: int = 3
        self.current_round: int = 0
        self.game_selection: str = "playlist"  # "playlist" (Mehrkampf), "host_choice", "random", "single"
        self.selected_game: str = "tictactoe"
        self.games_pool: List[str] = ["tictactoe", "connect4", "rps"]
        self.disciplines: List[str] = ["tictactoe", "connect4", "rps"]
        self.rewards: TournamentRewards = TournamentRewards()
        self.on_finished_callback: Optional[Callable[[Tournament], Any]] = None
        self.transition_info: Optional[Dict[str, Any]] = None
        self.points_win: int = 3
        self.points_draw: int = 1
        self.participants: Dict[str, TournamentPlayer] = {}
        self.active_matches: List[TournamentMatch] = []
        self.match_history: List[Dict[str, Any]] = []
        self.current_match_idx: int = 0
        self.spectated_match_id: Optional[str] = None
        self.last_round_result: Optional[Dict[str, Any]] = None
        self._finished_triggered: bool = False

        # Add initial host participant
        self.add_participant(host)

    def add_participant(self, player: Player) -> TournamentPlayer:
        if player.user_id not in self.participants:
            tp = TournamentPlayer(
                user_id=player.user_id,
                username=player.username,
                display_name=player.display_name,
                avatar_url=player.avatar_url,
                is_host=(player.user_id == self.host_id),
                connected=True
            )
            self.participants[player.user_id] = tp
            return tp
        else:
            tp = self.participants[player.user_id]
            tp.connected = True
            tp.username = player.username
            tp.display_name = player.display_name
            if player.avatar_url:
                tp.avatar_url = player.avatar_url
            if self.format != "knockout":
                tp.is_eliminated = False
            return tp

    def remove_participant(self, user_id: str, voluntary: bool = False) -> Optional[str]:
        if user_id not in self.participants:
            return None

        tp = self.participants[user_id]
        if self.status == "lobby":
            del self.participants[user_id]
            return None

        tp.connected = False
        if voluntary:
            tp.is_eliminated = True

        # If user is in the currently active match and voluntarily left, forfeit match to opponent
        curr_m = self.get_current_match()
        if voluntary and curr_m and curr_m.status == "active":
            if curr_m.player1.user_id == user_id:
                return curr_m.player2.user_id if curr_m.player2 else "draw"
            elif curr_m.player2 and curr_m.player2.user_id == user_id:
                return curr_m.player1.user_id

        return None

    def update_host(self, new_host_id: str) -> None:
        self.host_id = new_host_id
        for p in self.participants.values():
            p.is_host = (p.user_id == new_host_id)

    def get_current_match(self) -> Optional[TournamentMatch]:
        if not self.active_matches:
            return None
        if 0 <= self.current_match_idx < len(self.active_matches):
            return self.active_matches[self.current_match_idx]
        return self.active_matches[-1]

    def get_match_for_user(self, user_id: str) -> Optional[TournamentMatch]:
        for m in self.active_matches:
            if m.player1.user_id == user_id:
                return m
            if m.player2 and m.player2.user_id == user_id:
                return m
        return None

    def get_current_spectated_match(self) -> Optional[TournamentMatch]:
        return self.get_current_match()

    async def start_tournament(self, selected_game: Optional[str] = None) -> bool:
        if len(self.participants) < 2:
            return False

        if selected_game:
            self.selected_game = selected_game

        self.status = "active"
        self.current_round = 0
        self.match_history = []
        self._finished_triggered = False
        for p in self.participants.values():
            p.score = 0
            p.wins = 0
            p.losses = 0
            p.draws = 0
            p.is_eliminated = False

        if self.format == "knockout":
            self.total_rounds = max(1, math.ceil(math.log2(len(self.participants))))

        return await self.start_next_round(self.selected_game)

    def _create_game_instance(self, game_type: str, p1: TournamentPlayer, p2: Optional[TournamentPlayer]) -> Optional[BaseGame]:
        if not p2:
            return None
        from activities.games.connect4 import Connect4Game
        from activities.games.tictactoe import TicTacToeGame
        from activities.games.rps import RPSGame

        game_map = {
            "connect4": Connect4Game,
            "tictactoe": TicTacToeGame,
            "rps": RPSGame
        }
        cls = game_map.get(game_type, TicTacToeGame)
        host_player = Player(
            user_id=p1.user_id,
            username=p1.username,
            display_name=p1.display_name,
            avatar_url=p1.avatar_url,
            is_host=True
        )
        game = cls(session_id=self.session_id, host=host_player)
        guest_player = Player(
            user_id=p2.user_id,
            username=p2.username,
            display_name=p2.display_name,
            avatar_url=p2.avatar_url,
            is_host=False
        )
        game.add_player(guest_player)
        game.start_game()
        return game

    async def start_next_round(self, selected_game: Optional[str] = None) -> bool:
        if selected_game:
            self.selected_game = selected_game

        self.current_round += 1
        self.current_match_idx = 0
        self.active_matches = []

        # Eligible participants
        eligible = [p for p in self.participants.values() if not p.is_eliminated]
        if len(eligible) <= 1:
            self.status = "finished"
            await self._trigger_tournament_finished()
            return True

        # Shuffle for diverse pairings across rounds
        random.shuffle(eligible)

        # Game for this round
        if selected_game and selected_game in self.games_pool:
            chosen_game = selected_game
            self.selected_game = selected_game
        elif self.game_selection == "playlist" or self.selected_game == "playlist":
            disc_idx = (self.current_round - 1) % len(self.disciplines)
            chosen_game = self.disciplines[disc_idx]
            self.selected_game = chosen_game
        elif self.game_selection == "random" or self.selected_game == "random":
            chosen_game = random.choice(self.games_pool)
            self.selected_game = chosen_game
        else:
            chosen_game = self.selected_game if self.selected_game in self.games_pool else "connect4"

        matches: List[TournamentMatch] = []
        i = 0
        while i < len(eligible):
            p1 = eligible[i]
            if i + 1 < len(eligible):
                p2 = eligible[i + 1]
                game_inst = self._create_game_instance(chosen_game, p1, p2)
                match = TournamentMatch(
                    match_id=str(uuid.uuid4())[:8],
                    round_index=self.current_round,
                    game_type=chosen_game,
                    player1=p1,
                    player2=p2,
                    game_instance=game_inst
                )
                matches.append(match)
                i += 2
            else:
                # Odd player receives Bye
                match = TournamentMatch(
                    match_id=str(uuid.uuid4())[:8],
                    round_index=self.current_round,
                    game_type=chosen_game,
                    player1=p1,
                    player2=None,
                    game_instance=None
                )
                match.status = "finished"
                match.winner_id = p1.user_id
                if self.format == "knockout":
                    p1.wins += 1
                    p1.score += self.points_win
                else:
                    p1.score += self.points_draw
                matches.append(match)
                self.match_history.append({
                    "match_id": match.match_id,
                    "round": match.round_index,
                    "game_type": match.game_type,
                    "p1": match.player1.display_name,
                    "p2": "Freilos (Bye)",
                    "winner": match.player1.display_name
                })
                i += 1

        self.active_matches = matches
        if self.match_style == "parallel":
            has_active = False
            for m in self.active_matches:
                if m.status != "finished" and not m.is_bye:
                    m.status = "active"
                    has_active = True
            if has_active:
                self.status = "active"
                first_active = next((m for m in self.active_matches if m.status == "active"), None)
                if first_active:
                    self.spectated_match_id = first_active.match_id
                    self.current_match_idx = self.active_matches.index(first_active)
            elif self.active_matches:
                self.spectated_match_id = None
                self.current_match_idx = 0
                self.status = "round_end"
            else:
                self.status = "finished"
        else:
            first_playable = next((m for m in self.active_matches if m.status != "finished" and not m.is_bye), None)
            if first_playable:
                first_playable.status = "active"
                self.spectated_match_id = first_playable.match_id
                self.current_match_idx = self.active_matches.index(first_playable)
                self.status = "active"
            elif self.active_matches:
                self.spectated_match_id = None
                self.current_match_idx = 0
                self.status = "round_end"
            else:
                self.status = "finished"

        return True

    async def resolve_current_match(self, winner: str) -> None:
        curr_m = self.get_current_match()
        if not curr_m:
            return
        await self._resolve_match(curr_m, winner)

    async def _resolve_match(self, match: TournamentMatch, winner: str) -> None:
        match.status = "finished"
        match.winner_id = winner

        if winner == "draw":
            match.player1.score += self.points_draw
            match.player1.draws += 1
            if match.player2:
                match.player2.score += self.points_draw
                match.player2.draws += 1
        elif winner == match.player1.user_id:
            match.player1.score += self.points_win
            match.player1.wins += 1
            if match.player2:
                match.player2.losses += 1
                if self.format == "knockout":
                    match.player2.is_eliminated = True
        elif match.player2 and winner == match.player2.user_id:
            match.player2.score += self.points_win
            match.player2.wins += 1
            match.player1.losses += 1
            if self.format == "knockout":
                match.player1.is_eliminated = True

        # Archive into history
        winner_name = winner
        if winner == match.player1.user_id:
            winner_name = match.player1.display_name
        elif match.player2 and winner == match.player2.user_id:
            winner_name = match.player2.display_name
        elif winner == "draw":
            winner_name = "draw"

        self.match_history.append({
            "match_id": match.match_id,
            "round": match.round_index,
            "game_type": match.game_type,
            "p1": match.player1.display_name,
            "p2": match.player2.display_name if match.player2 else "Freilos (Bye)",
            "winner": winner_name
        })

        # Check if entire round is completed
        all_finished = all(m.status == "finished" for m in self.active_matches)
        if all_finished:
            self.transition_info = None
            if self.format == "knockout":
                remaining = [p for p in self.participants.values() if not p.is_eliminated]
                if len(remaining) <= 1:
                    self.status = "finished"
                else:
                    self.status = "round_end"
            else:
                remaining = [p for p in self.participants.values() if not p.is_eliminated]
                if len(remaining) <= 1 or self.current_round >= self.total_rounds:
                    self.status = "finished"
                else:
                    self.status = "round_end"
            if self.status == "finished":
                await self._trigger_tournament_finished()
        else:
            next_idx = self.current_match_idx + 1
            if next_idx < len(self.active_matches):
                next_m = self.active_matches[next_idx]
                self.transition_info = {
                    "active": True,
                    "seconds_remaining": 5,
                    "prev_winner": winner_name,
                    "next_match_id": next_m.match_id,
                    "next_p1": next_m.player1.display_name,
                    "next_p2": next_m.player2.display_name if next_m.player2 else "Freilos (Bye)",
                    "next_game": next_m.game_type
                }

    async def _trigger_tournament_finished(self) -> None:
        if self._finished_triggered:
            return
        self._finished_triggered = True
        if self.on_finished_callback:
            try:
                res = self.on_finished_callback(self)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                logger.error("Error executing tournament on_finished_callback: %s", e)

    async def advance_to_next_match(self) -> Optional[TournamentMatch]:
        self.transition_info = None
        curr = self.get_current_match()
        if curr and curr.status == "active":
            return curr
        while self.current_match_idx + 1 < len(self.active_matches):
            self.current_match_idx += 1
            next_m = self.active_matches[self.current_match_idx]
            if next_m.is_bye or next_m.status == "finished":
                continue
            next_m.status = "active"
            self.spectated_match_id = next_m.match_id
            return next_m

        # If no further playable matches exist in this round:
        all_finished = all(m.status == "finished" for m in self.active_matches)
        if all_finished:
            remaining = [p for p in self.participants.values() if not p.is_eliminated]
            if len(remaining) <= 1:
                self.status = "finished"
            elif self.format == "knockout":
                self.status = "round_end"
            else:
                if self.current_round >= self.total_rounds:
                    self.status = "finished"
                else:
                    self.status = "round_end"
            if self.status == "finished":
                await self._trigger_tournament_finished()

        return None

    async def handle_match_action(self, user_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        match = self.get_match_for_user(user_id) or self.get_current_match()
        if not match or not match.game_instance:
            return {"error": "No active match found"}

        if match.status != "active":
            return {"error": "Match is not active"}

        sub_action = data.get("sub_action", "move")
        sub_data = data.get("sub_data", data)
        result = await match.game_instance.handle_action(user_id, sub_action, sub_data)

        if match.game_instance.is_finished:
            winner = match.game_instance.winner or "draw"
            await self._resolve_match(match, winner)

        return {"status": "success", "result": result}

    async def handle_action(self, user_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        is_host = (user_id == self.host_id)

        if action == "tournament_update_settings":
            if not is_host:
                return {"error": "Only tournament host can change settings"}
            if "format" in data:
                self.format = data["format"]
            if "match_style" in data:
                if data["match_style"] in ("spectated", "parallel"):
                    self.match_style = data["match_style"]
            if "total_rounds" in data:
                self.total_rounds = max(1, min(50, int(data["total_rounds"])))
            if "game_selection" in data:
                self.game_selection = data["game_selection"]
            if "disciplines" in data and isinstance(data["disciplines"], list):
                valid_discs = [d for d in data["disciplines"] if d in self.games_pool]
                if valid_discs:
                    self.disciplines = valid_discs
            if "selected_game" in data:
                self.selected_game = data["selected_game"]
            if "points_win" in data:
                self.points_win = max(1, min(10, int(data["points_win"])))
            if "points_draw" in data:
                self.points_draw = max(0, min(5, int(data["points_draw"])))
            if "title" in data:
                self.title = str(data["title"])[:32]
            return {"status": "settings_updated"}

        if action == "tournament_start":
            if not is_host:
                return {"error": "Only host can start tournament"}
            if "selected_game" in data:
                self.selected_game = data["selected_game"]
            ok = await self.start_tournament(self.selected_game)
            if not ok:
                return {"error": "Mindestens 2 Teilnehmer werden für ein Turnier benötigt!"}
            return {"status": "tournament_started"}

        if action == "tournament_next_round":
            if not is_host:
                return {"error": "Only host can advance round"}
            if self.status not in ("round_end", "finished"):
                return {"error": "Current round is not finished yet"}
            selected = data.get("selected_game") or self.selected_game
            self.selected_game = selected
            if self.current_round >= self.total_rounds:
                self.total_rounds = self.current_round + 1
            self.status = "active"
            self._finished_triggered = False
            await self.start_next_round(selected)
            return {"status": "next_round_started"}

        if action == "tournament_add_round":
            if not is_host:
                return {"error": "Only host can add rounds"}
            self.total_rounds = max(self.total_rounds, self.current_round) + 1
            if self.status == "finished":
                self.status = "round_end"
                self._finished_triggered = False
            return {"status": "round_added", "total_rounds": self.total_rounds}

        if action in ("tournament_next_match", "tournament_advance_match"):
            if not is_host:
                return {"error": "Only host can advance match"}
            await self.advance_to_next_match()
            return {"status": "next_match_started"}

        if action == "tournament_reset_to_lobby":
            if not is_host:
                return {"error": "Only host can reset tournament to lobby"}
            self.status = "lobby"
            self.current_round = 0
            self.active_matches = []
            self.transition_info = None
            self._finished_triggered = False
            self.rewards.rewards_granted = False
            for p in self.participants.values():
                p.score = 0
                p.wins = 0
                p.losses = 0
                p.draws = 0
                p.is_eliminated = False
            return {"status": "reset_to_lobby"}

        if action in ("tournament_end", "tournament_finish"):
            if not is_host:
                return {"error": "Only host can end tournament"}
            self.status = "finished"
            self.transition_info = None
            await self._trigger_tournament_finished()
            return {"status": "tournament_finished"}

        if action == "tournament_cheer":
            emote = str(data.get("emote", "🎉"))[:8]
            p = self.participants.get(user_id)
            name = p.display_name if p else "Zuschauer"
            current_m = self.get_current_match()
            if current_m:
                current_m.cheers.append({"user_id": user_id, "name": name, "emote": emote})
                if len(current_m.cheers) > 15:
                    current_m.cheers.pop(0)
            return {"status": "cheered"}

        if action == "tournament_match_action":
            return await self.handle_match_action(user_id, action, data)

        return {"error": f"Unknown tournament action: {action}"}

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        sorted_p = sorted(
            self.participants.values(),
            key=lambda p: (p.score, p.wins, -p.losses),
            reverse=True
        )
        return [
            {
                "rank": idx + 1,
                "user_id": p.user_id,
                "display_name": p.display_name,
                "avatar_url": p.avatar_url,
                "score": p.score,
                "wins": p.wins,
                "losses": p.losses,
                "draws": p.draws,
                "is_eliminated": p.is_eliminated,
                "is_host": p.is_host
            }
            for idx, p in enumerate(sorted_p)
        ]

    def get_podium(self) -> List[Dict[str, Any]]:
        board = self.get_leaderboard()
        medals = ["🥇", "🥈", "🥉"]
        podium = []
        for i, item in enumerate(board[:3]):
            entry = dict(item)
            entry["medal"] = medals[i]
            podium.append(entry)
        return podium

    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        curr_m = (self.get_match_for_user(for_user_id) if (for_user_id and self.match_style == "parallel") else None) or self.get_current_match()
        curr_match_data = None
        if curr_m:
            curr_match_data = {
                "match_id": curr_m.match_id,
                "round_index": curr_m.round_index,
                "game_type": curr_m.game_type,
                "p1_id": curr_m.player1.user_id,
                "p2_id": curr_m.player2.user_id if curr_m.player2 else None,
                "p1_name": curr_m.player1.display_name,
                "p2_name": curr_m.player2.display_name if curr_m.player2 else "Freilos (Bye)",
                "p1_avatar": curr_m.player1.avatar_url,
                "p2_avatar": curr_m.player2.avatar_url if curr_m.player2 else None,
                "status": curr_m.status,
                "winner": curr_m.winner_id,
                "cheers": curr_m.cheers[-8:]
            }

        matches_summary = [
            {
                "match_id": m.match_id,
                "p1_name": m.player1.display_name,
                "p2_name": m.player2.display_name if m.player2 else "Freilos (Bye)",
                "game_type": m.game_type,
                "status": m.status,
                "winner": m.winner_id,
                "is_active": (curr_m is not None and m.match_id == curr_m.match_id)
            }
            for m in self.active_matches
        ]

        return {
            "session_id": self.session_id,
            "host_id": self.host_id,
            "host_name": self.participants.get(self.host_id).display_name if self.host_id in self.participants else "Host",
            "is_participant": (for_user_id in self.participants) if for_user_id else False,
            "title": self.title,
            "status": self.status,
            "format": self.format,
            "match_style": self.match_style,
            "total_rounds": self.total_rounds,
            "current_round": self.current_round,
            "game_selection": self.game_selection,
            "selected_game": self.selected_game,
            "games_pool": self.games_pool,
            "disciplines": self.disciplines,
            "rewards": self.rewards.model_dump(),
            "transition_info": self.transition_info,
            "points_win": self.points_win,
            "points_draw": self.points_draw,
            "participants_count": len(self.participants),
            "leaderboard": self.get_leaderboard(),
            "podium": self.get_podium(),
            "active_matches": matches_summary,
            "current_match": curr_match_data,
            "match_history": self.match_history[-10:]
        }
