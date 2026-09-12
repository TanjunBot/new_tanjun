from __future__ import annotations

import asyncio
import copy
import random
from typing import Any, Dict, List, Optional
from activities.base import BaseGame, Player, serialized_action


class RPSGame(BaseGame):
    """Rock-Paper-Scissors (Schere Stein Papier) with hidden picks, series modes, variants, PvP & Bot AI."""

    CLASSIC_CHOICES = ["rock", "paper", "scissors"]
    EXTENDED_CHOICES = ["rock", "paper", "scissors", "lizard", "spock"]

    CLASSIC_WIN_MAP: Dict[str, List[str]] = {
        "rock": ["scissors"],
        "paper": ["rock"],
        "scissors": ["paper"]
    }

    EXTENDED_WIN_MAP: Dict[str, List[str]] = {
        "rock": ["scissors", "lizard"],
        "paper": ["rock", "spock"],
        "scissors": ["paper", "lizard"],
        "lizard": ["spock", "paper"],
        "spock": ["scissors", "rock"]
    }

    def __init__(self, session_id: str, host: Player, difficulty: int = 3) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.difficulty: int = difficulty
        self.target_wins: int = 3  # Best of 5 (first to 3)
        self.variation: str = "classic"  # "classic" or "lizard_spock"
        self.current_round: int = 1
        self.scores: Dict[str, int] = {}
        self.current_picks: Dict[str, str] = {}  # user_id -> choice
        self.last_round_result: Optional[Dict[str, Any]] = None
        self.round_history: List[Dict[str, Any]] = []
        self.bot_player: Optional[Player] = None

    @property
    def game_type(self) -> str:
        return "rps"

    @property
    def display_name(self) -> str:
        return "Schere Stein Papier"

    @property
    def choices(self) -> List[str]:
        return self.EXTENDED_CHOICES if self.variation == "lizard_spock" else self.CLASSIC_CHOICES

    @property
    def win_map(self) -> Dict[str, List[str]]:
        return self.EXTENDED_WIN_MAP if self.variation == "lizard_spock" else self.CLASSIC_WIN_MAP

    def setup_bot(self, difficulty: int = 3) -> None:
        self.difficulty = max(1, min(5, difficulty))
        self.game_mode = "bot"
        self.bot_player = Player(
            user_id="bot_tanjun",
            username="TanjunBot",
            display_name="Tanjun AI",
            avatar_url="/static/images/tanjun_avatar.png",
            is_bot=True,
            is_host=False,
            connected=True
        )
        self.players["bot_tanjun"] = self.bot_player

    def start_game(self) -> bool:
        p_ids = list(self.players.keys())
        if len(p_ids) == 1 and self.game_mode == "bot":
            self.setup_bot(self.difficulty)
            p_ids = list(self.players.keys())

        if len(p_ids) < 2:
            return False

        self.is_started = True
        self.is_finished = False
        self.winner = None
        self.current_round = 1
        self.current_picks = {}
        self.last_round_result = None
        self.round_history = []
        self.scores = {pid: 0 for pid in p_ids}
        return True

    def _bot_pick(self, human_id: str) -> str:
        available = self.choices
        # Pattern-based AI or random depending on difficulty
        if self.difficulty >= 3 and self.round_history:
            last_human_pick = None
            for r in reversed(self.round_history):
                if human_id in r.get("picks", {}):
                    last_human_pick = r["picks"][human_id]
                    break
            if last_human_pick and random.random() < 0.65:
                # Find moves that beat the last human pick
                beating_moves = [move for move, beats in self.win_map.items() if last_human_pick in beats]
                if beating_moves:
                    return random.choice(beating_moves)

        return random.choice(available)

    def _evaluate_round(self) -> Dict[str, Any]:
        p_ids = list(self.players.keys())[:2]
        p1_id, p2_id = p_ids[0], p_ids[1]
        c1 = self.current_picks.get(p1_id, "")
        c2 = self.current_picks.get(p2_id, "")

        round_winner: Optional[str] = None
        if c1 == c2:
            round_winner = "draw"
        elif c2 in self.win_map.get(c1, []):
            round_winner = p1_id
            self.scores[p1_id] = self.scores.get(p1_id, 0) + 1
        else:
            round_winner = p2_id
            self.scores[p2_id] = self.scores.get(p2_id, 0) + 1

        result = {
            "round": self.current_round,
            "picks": {p1_id: c1, p2_id: c2},
            "winner": round_winner
        }
        self.round_history.append(result)
        self.last_round_result = result
        self.current_picks = {}

        # Check match win
        if self.scores.get(p1_id, 0) >= self.target_wins:
            self.is_finished = True
            self.winner = p1_id
        elif self.scores.get(p2_id, 0) >= self.target_wins:
            self.is_finished = True
            self.winner = p2_id
        else:
            self.current_round += 1

        return result

    @serialized_action
    async def handle_action(
        self,
        player_id: str,
        action: str,
        data: Dict[str, Any],
        broadcast_cb: Optional[Any] = None
    ) -> Dict[str, Any]:
        if action == "start":
            if not self.is_controller(player_id):
                return {"error": "Only the host can start or configure the game"}
            mode = data.get("mode", "pvp")
            if mode not in {"pvp", "bot"}:
                return {"error": "Invalid game mode"}
            if mode != self.game_mode:
                self.scores = {pid: 0 for pid in self.players}
            self.game_mode = mode
            try:
                difficulty = int(data.get("difficulty", 3))
                target_wins = int(data.get("target_wins", 3))
            except (TypeError, ValueError):
                return {"error": "Invalid match configuration"}
            if not 1 <= target_wins <= 100:
                return {"error": "Target wins must be between 1 and 100"}
            variation = data.get("variation", "classic")
            if variation not in {"classic", "lizard_spock"}:
                return {"error": "Invalid variation"}
            self.difficulty = max(1, min(5, difficulty))
            self.target_wins = target_wins
            self.variation = variation
            if mode == "bot":
                self.setup_bot(self.difficulty)
            elif "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None

            started = self.start_game()
            if not started:
                return {
                    "error": "Mindestens 2 Spieler werden für PvP benötigt.",
                    "status": "waiting_for_players",
                    "state": self.get_state()
                }
            return {"status": "started", "state": self.get_state()}

        if action == "pick":
            if not self.is_started or self.is_finished:
                return {"error": "Game is not active"}

            active_pids = list(self.players.keys())[:2]
            if player_id not in active_pids or player_id in self.spectators:
                return {"error": "Only active players can make picks"}

            choice = data.get("choice")
            if not isinstance(choice, str) or choice not in self.choices:
                return {"error": f"Invalid choice: {choice}"}
            if player_id in self.current_picks:
                return {"error": "You have already picked this round"}

            self.current_picks[player_id] = choice

            round_completed = False
            round_result = None

            # If vs bot, bot has a natural thinking pause before evaluating
            if self.game_mode == "bot" and "bot_tanjun" in self.players:
                if broadcast_cb:
                    await broadcast_cb()
                await asyncio.sleep(0.55)
                bot_choice = self._bot_pick(player_id)
                self.current_picks["bot_tanjun"] = bot_choice
                round_result = self._evaluate_round()
                round_completed = True
            else:
                # Check if all active human players have picked
                human_pids = [p for p in active_pids if not self.players[p].is_bot]
                if all(pid in self.current_picks for pid in human_pids):
                    round_result = self._evaluate_round()
                    round_completed = True

            return {
                "status": "picked",
                "round_completed": round_completed,
                "round_result": round_result,
                "state": self.get_state(for_user_id=player_id)
            }

        if action == "restart":
            if not self.is_controller(player_id):
                return {"error": "Only the host can restart the game"}
            self.is_started = False
            self.start_game()
            return {"status": "restarted", "state": self.get_state()}

        if action == "lobby":
            if not self.is_controller(player_id):
                return {"error": "Only the host can return to the lobby"}
            self.is_started = False
            self.is_finished = False
            self.winner = None
            self.current_picks = {}
            self.last_round_result = None
            self.round_history = []
            if "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None
            self.scores = {pid: 0 for pid in self.players}
            return {"status": "lobby", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.is_started = False
        self.is_finished = False
        self.winner = None
        self.current_round = 1
        self.current_picks = {}
        self.last_round_result = None
        self.round_history = []
        self.scores = {pid: 0 for pid in self.players}

    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        # Mask opponents' choices until round evaluation
        visible_picks: Dict[str, str] = {}
        for pid, choice in self.current_picks.items():
            if for_user_id is not None and pid == for_user_id:
                visible_picks[pid] = choice
            else:
                visible_picks[pid] = "locked"

        return {
            "session_id": self.session_id,
            "game_type": self.game_type,
            "game_mode": self.game_mode,
            "difficulty": self.difficulty,
            "target_wins": self.target_wins,
            "variation": self.variation,
            "available_choices": self.choices,
            "current_round": self.current_round,
            "is_started": self.is_started,
            "is_finished": self.is_finished,
            "winner": self.winner,
            "current_picks": dict(visible_picks),
            "last_round_result": copy.deepcopy(self.last_round_result),
            "round_history": copy.deepcopy(self.round_history),
            "scores": dict(self.scores),
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
