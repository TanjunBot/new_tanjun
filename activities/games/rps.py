from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional
from activities.base import BaseGame, Player


class RPSGame(BaseGame):
    """Rock-Paper-Scissors (Schere Stein Papier) with hidden picks, best-of series, PvP & Bot AI."""

    CHOICES = ["rock", "paper", "scissors"]
    WIN_MAP = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    def __init__(self, session_id: str, host: Player, difficulty: int = 3) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.difficulty: int = difficulty
        self.target_wins: int = 3  # Best of 5 (first to 3)
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
        # Pattern-based AI or random depending on difficulty
        if self.difficulty >= 4 and self.round_history:
            # Predict human might switch or repeat
            last_human_pick = None
            for r in reversed(self.round_history):
                if human_id in r.get("picks", {}):
                    last_human_pick = r["picks"][human_id]
                    break
            if last_human_pick and random.random() < 0.6:
                # Counter what would beat the last pick
                counter = {"rock": "paper", "paper": "scissors", "scissors": "rock"}
                return counter.get(last_human_pick, random.choice(self.CHOICES))

        return random.choice(self.CHOICES)

    def _evaluate_round(self) -> Dict[str, Any]:
        p_ids = list(self.players.keys())
        p1_id, p2_id = p_ids[0], p_ids[1]
        c1 = self.current_picks.get(p1_id, "")
        c2 = self.current_picks.get(p2_id, "")

        round_winner: Optional[str] = None
        if c1 == c2:
            round_winner = "draw"
        elif self.WIN_MAP.get(c1) == c2:
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

    async def handle_action(self, player_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "start":
            mode = data.get("mode", "pvp")
            self.game_mode = mode
            self.difficulty = int(data.get("difficulty", 3))
            self.target_wins = int(data.get("target_wins", 3))
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

            choice = data.get("choice")
            if choice not in self.CHOICES:
                return {"error": f"Invalid choice: {choice}"}

            self.current_picks[player_id] = choice

            round_completed = False
            round_result = None

            # If vs bot, bot picks immediately
            if self.game_mode == "bot" and "bot_tanjun" in self.players:
                bot_choice = self._bot_pick(player_id)
                self.current_picks["bot_tanjun"] = bot_choice
                round_result = self._evaluate_round()
                round_completed = True
            else:
                # Check if all human players have picked
                human_pids = [p for p in self.players.keys() if not self.players[p].is_bot]
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
            return await self.handle_action(player_id, "start", {
                "mode": self.game_mode,
                "difficulty": self.difficulty,
                "target_wins": self.target_wins
            })

        if action == "lobby":
            self.is_started = False
            self.is_finished = False
            self.winner = None
            self.current_picks = {}
            self.last_round_result = None
            self.round_history = []
            if "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None
            return {"status": "lobby", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.is_started = False
        self.is_finished = False
        self.winner = None
        self.current_picks = {}
        self.last_round_result = None
        self.round_history = []
        self.scores = {pid: 0 for pid in self.players}

    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        # Mask choices until round is evaluated: each player only sees IF others picked, not WHAT
        masked_picks = {}
        for uid, choice in self.current_picks.items():
            if uid == for_user_id or self.last_round_result is not None:
                masked_picks[uid] = choice
            else:
                masked_picks[uid] = "locked"

        return {
            "session_id": self.session_id,
            "game_type": self.game_type,
            "game_mode": self.game_mode,
            "difficulty": self.difficulty,
            "target_wins": self.target_wins,
            "current_round": self.current_round,
            "is_started": self.is_started,
            "is_finished": self.is_finished,
            "winner": self.winner,
            "current_picks": masked_picks,
            "last_round_result": self.last_round_result,
            "round_history": self.round_history,
            "scores": self.scores,
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
