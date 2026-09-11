from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional, Tuple
from activities.base import BaseGame, Player


class Connect4Game(BaseGame):
    """Connect 4 (Vier Gewinnt) implementation with 7x6 grid, PvP & Bot AI."""

    ROWS = 6
    COLS = 7

    def __init__(self, session_id: str, host: Player, difficulty: int = 3) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.board: List[str] = [""] * (self.ROWS * self.COLS)
        self.difficulty: int = difficulty
        self.current_turn: Optional[str] = None
        self.player_symbols: Dict[str, str] = {}  # user_id -> "R" (Red) or "Y" (Yellow)
        self.winning_line: Optional[List[int]] = None
        self.scores: Dict[str, int] = {}
        self.bot_player: Optional[Player] = None

    @property
    def game_type(self) -> str:
        return "connect4"

    @property
    def display_name(self) -> str:
        return "Vier Gewinnt"

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

        self.board = [""] * (self.ROWS * self.COLS)
        self.is_started = True
        self.is_finished = False
        self.winner = None
        self.winning_line = None

        self.player_symbols = {
            p_ids[0]: "R",
            p_ids[1]: "Y"
        }
        for pid in p_ids:
            if pid not in self.scores:
                self.scores[pid] = 0

        self.current_turn = p_ids[0]
        return True

    def _get_lowest_empty_row(self, col: int, board: Optional[List[str]] = None) -> int:
        b = board if board is not None else self.board
        for row in range(self.ROWS - 1, -1, -1):
            if b[row * self.COLS + col] == "":
                return row
        return -1

    def check_winner(self, b: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[List[int]]]:
        board = b if b is not None else self.board

        # Horizontal check
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                idx = r * self.COLS + c
                s = board[idx]
                if s and s == board[idx + 1] == board[idx + 2] == board[idx + 3]:
                    return s, [idx, idx + 1, idx + 2, idx + 3]

        # Vertical check
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                idx = r * self.COLS + c
                s = board[idx]
                if s and s == board[idx + self.COLS] == board[idx + 2 * self.COLS] == board[idx + 3 * self.COLS]:
                    return s, [idx, idx + self.COLS, idx + 2 * self.COLS, idx + 3 * self.COLS]

        # Diagonal (top-left to bottom-right \)
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                idx = r * self.COLS + c
                s = board[idx]
                step = self.COLS + 1
                if s and s == board[idx + step] == board[idx + 2 * step] == board[idx + 3 * step]:
                    return s, [idx, idx + step, idx + 2 * step, idx + 3 * step]

        # Diagonal (bottom-left to top-right /)
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                idx = r * self.COLS + c
                s = board[idx]
                step = self.COLS - 1
                if s and s == board[idx - step] == board[idx - 2 * step] == board[idx - 3 * step]:
                    return s, [idx, idx - step, idx - 2 * step, idx - 3 * step]

        if all(cell != "" for cell in board):
            return "draw", None

        return None, None

    def _bot_calculate_move(self) -> int:
        valid_cols = [c for c in range(self.COLS) if self._get_lowest_empty_row(c) != -1]
        if not valid_cols:
            return -1

        # Difficulty random chance
        random_chance = {1: 0.75, 2: 0.5, 3: 0.25, 4: 0.1, 5: 0.0}.get(self.difficulty, 0.25)
        if random.random() < random_chance:
            return random.choice(valid_cols)

        bot_sym = self.player_symbols.get("bot_tanjun", "Y")
        human_sym = "R" if bot_sym == "Y" else "Y"

        # 1. Check if bot can win immediately
        for c in valid_cols:
            r = self._get_lowest_empty_row(c)
            idx = r * self.COLS + c
            self.board[idx] = bot_sym
            w, _ = self.check_winner()
            self.board[idx] = ""
            if w == bot_sym:
                return c

        # 2. Check if human can win on next turn and block
        for c in valid_cols:
            r = self._get_lowest_empty_row(c)
            idx = r * self.COLS + c
            self.board[idx] = human_sym
            w, _ = self.check_winner()
            self.board[idx] = ""
            if w == human_sym:
                return c

        # 3. Prefer center column or inner columns
        preference_order = [3, 2, 4, 1, 5, 0, 6]
        for pref in preference_order:
            if pref in valid_cols and random.random() < 0.7:
                return pref

        return random.choice(valid_cols)

    async def handle_action(self, player_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "start":
            mode = data.get("mode", "pvp")
            self.game_mode = mode
            diff = int(data.get("difficulty", 3))
            self.difficulty = diff
            if mode == "bot":
                self.setup_bot(diff)
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

        if action == "move":
            if not self.is_started or self.is_finished:
                return {"error": "Game is not active"}
            if self.current_turn != player_id:
                return {"error": "Not your turn"}

            col = data.get("col") if "col" in data else data.get("column")
            if col is None or not (0 <= col < self.COLS):
                return {"error": "Invalid column"}

            row = self._get_lowest_empty_row(col)
            if row == -1:
                return {"error": "Column is full"}

            idx = row * self.COLS + col
            sym = self.player_symbols.get(player_id)
            if not sym:
                return {"error": "Unknown player"}

            self.board[idx] = sym

            winner_sym, line = self.check_winner()
            if winner_sym:
                self.is_finished = True
                self.winning_line = line
                if winner_sym == "draw":
                    self.winner = "draw"
                else:
                    self.winner = player_id
                    self.scores[player_id] = self.scores.get(player_id, 0) + 1
            else:
                p_ids = list(self.players.keys())
                next_player = p_ids[1] if self.current_turn == p_ids[0] else p_ids[0]
                self.current_turn = next_player

                if next_player == "bot_tanjun" and not self.is_finished:
                    await asyncio.sleep(0.4)
                    bot_col = self._bot_calculate_move()
                    if bot_col != -1:
                        bot_row = self._get_lowest_empty_row(bot_col)
                        if bot_row != -1:
                            bot_idx = bot_row * self.COLS + bot_col
                            bot_sym = self.player_symbols.get("bot_tanjun", "Y")
                            self.board[bot_idx] = bot_sym
                            b_winner, b_line = self.check_winner()
                            if b_winner:
                                self.is_finished = True
                                self.winning_line = b_line
                                if b_winner == "draw":
                                    self.winner = "draw"
                                else:
                                    self.winner = "bot_tanjun"
                                    self.scores["bot_tanjun"] = self.scores.get("bot_tanjun", 0) + 1
                            else:
                                self.current_turn = player_id

            return {"status": "moved", "state": self.get_state()}

        if action == "restart":
            self.board = [""] * (self.ROWS * self.COLS)
            self.is_finished = False
            self.winning_line = None
            self.winner = None
            p_ids = list(self.players.keys())
            if len(p_ids) >= 2:
                self.current_turn = p_ids[0] if random.random() > 0.5 else p_ids[1]
                if self.current_turn == "bot_tanjun":
                    bot_col = self._bot_calculate_move()
                    if bot_col != -1:
                        bot_row = self._get_lowest_empty_row(bot_col)
                        if bot_row != -1:
                            self.board[bot_row * self.COLS + bot_col] = self.player_symbols.get("bot_tanjun", "Y")
                            self.current_turn = p_ids[0] if p_ids[1] == "bot_tanjun" else p_ids[1]
            return {"status": "restarted", "state": self.get_state()}

        if action == "lobby":
            self.board = [""] * (self.ROWS * self.COLS)
            self.is_started = False
            self.is_finished = False
            self.winner = None
            self.winning_line = None
            if "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None
            return {"status": "lobby", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.board = [""] * (self.ROWS * self.COLS)
        self.is_started = False
        self.is_finished = False
        self.winner = None
        self.winning_line = None
        self.scores = {pid: 0 for pid in self.players}

    def get_state(self, for_user_id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "game_type": self.game_type,
            "game_mode": self.game_mode,
            "difficulty": self.difficulty,
            "is_started": self.is_started,
            "is_finished": self.is_finished,
            "winner": self.winner,
            "winning_line": self.winning_line,
            "board": self.board,
            "rows": self.ROWS,
            "cols": self.COLS,
            "current_turn": self.current_turn,
            "player_symbols": self.player_symbols,
            "scores": self.scores,
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
