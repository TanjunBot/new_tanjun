from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional, Tuple
from activities.base import BaseGame, Player


class Connect4Game(BaseGame):
    """Connect 4 (Vier Gewinnt) with dynamic grid size, custom connect targets, PvP & Bot AI."""

    DEFAULT_ROWS = 6
    DEFAULT_COLS = 7

    def __init__(
        self,
        session_id: str,
        host: Player,
        difficulty: int = 3,
        rows: int = 6,
        cols: int = 7,
        connect_target: int = 4
    ) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.rows: int = rows
        self.cols: int = cols
        self.connect_target: int = connect_target
        self.first_turn_rule: str = "host"
        self.board: List[str] = [""] * (self.rows * self.cols)
        self.difficulty: int = difficulty
        self.current_turn: Optional[str] = None
        self.player_symbols: Dict[str, str] = {}  # user_id -> "R" (Red) or "Y" (Yellow)
        self.winning_line: Optional[List[int]] = None
        self.scores: Dict[str, int] = {}
        self.bot_player: Optional[Player] = None
        self.last_move: Optional[int] = None

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

        self.board = [""] * (self.rows * self.cols)
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

        # Decide who starts
        if self.first_turn_rule == "random":
            self.current_turn = random.choice(p_ids)
        elif self.first_turn_rule == "guest" and len(p_ids) > 1:
            self.current_turn = p_ids[1]
        else:
            self.current_turn = p_ids[0]

        # If bot plays first, make move
        if self.current_turn == "bot_tanjun":
            bot_col = self._bot_calculate_move()
            if bot_col != -1:
                r = self._get_lowest_empty_row(bot_col)
                if r != -1:
                    bot_idx = r * self.cols + bot_col
                    self.board[bot_idx] = self.player_symbols.get("bot_tanjun", "Y")
                    self.last_move = bot_idx
                    self.current_turn = p_ids[0]

        return True

    def _get_lowest_empty_row(self, col: int, board: Optional[List[str]] = None) -> int:
        b = board if board is not None else self.board
        for row in range(self.rows - 1, -1, -1):
            if b[row * self.cols + col] == "":
                return row
        return -1

    def check_winner(self, b: Optional[List[str]] = None) -> Tuple[Optional[str], Optional[List[int]]]:
        board = b if b is not None else self.board
        k = self.connect_target

        # Horizontal check
        for r in range(self.rows):
            for c in range(self.cols - k + 1):
                idx = r * self.cols + c
                s = board[idx]
                if s and all(board[idx + i] == s for i in range(1, k)):
                    return s, [idx + i for i in range(k)]

        # Vertical check
        for r in range(self.rows - k + 1):
            for c in range(self.cols):
                idx = r * self.cols + c
                s = board[idx]
                if s and all(board[idx + i * self.cols] == s for i in range(1, k)):
                    return s, [idx + i * self.cols for i in range(k)]

        # Diagonal (top-left to bottom-right \)
        step_diag1 = self.cols + 1
        for r in range(self.rows - k + 1):
            for c in range(self.cols - k + 1):
                idx = r * self.cols + c
                s = board[idx]
                if s and all(board[idx + i * step_diag1] == s for i in range(1, k)):
                    return s, [idx + i * step_diag1 for i in range(k)]

        # Diagonal (bottom-left to top-right /)
        step_diag2 = self.cols - 1
        for r in range(k - 1, self.rows):
            for c in range(self.cols - k + 1):
                idx = r * self.cols + c
                s = board[idx]
                if s and all(board[idx - i * step_diag2] == s for i in range(1, k)):
                    return s, [idx - i * step_diag2 for i in range(k)]

        if all(cell != "" for cell in board):
            return "draw", None

        return None, None

    def _bot_calculate_move(self) -> int:
        valid_cols = [c for c in range(self.cols) if self._get_lowest_empty_row(c) != -1]
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
            idx = r * self.cols + c
            self.board[idx] = bot_sym
            w, _ = self.check_winner()
            self.board[idx] = ""
            if w == bot_sym:
                return c

        # 2. Check if human can win on next turn and block
        for c in valid_cols:
            r = self._get_lowest_empty_row(c)
            idx = r * self.cols + c
            self.board[idx] = human_sym
            w, _ = self.check_winner()
            self.board[idx] = ""
            if w == human_sym:
                return c

        # 3. Prefer center column or inner columns
        center = self.cols // 2
        preference_order = sorted(range(self.cols), key=lambda col: abs(col - center))
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

            # Configurable grid and rules
            rows = int(data.get("rows", self.DEFAULT_ROWS))
            cols = int(data.get("cols", self.DEFAULT_COLS))
            self.rows = max(5, min(9, rows))
            self.cols = max(6, min(10, cols))
            self.connect_target = max(3, min(5, int(data.get("connect", 4))))
            self.first_turn_rule = data.get("first_turn", "host")

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
            if col is None or not (0 <= col < self.cols):
                return {"error": "Invalid column"}

            row = self._get_lowest_empty_row(col)
            if row == -1:
                return {"error": "Column is full"}

            idx = row * self.cols + col
            sym = self.player_symbols.get(player_id)
            if not sym:
                return {"error": "Unknown player"}

            self.board[idx] = sym
            self.last_move = idx

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
                    await asyncio.sleep(0.55)
                    bot_col = self._bot_calculate_move()
                    if bot_col != -1:
                        bot_row = self._get_lowest_empty_row(bot_col)
                        if bot_row != -1:
                            bot_idx = bot_row * self.cols + bot_col
                            bot_sym = self.player_symbols.get("bot_tanjun", "Y")
                            self.board[bot_idx] = bot_sym
                            self.last_move = bot_idx
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
            self.board = [""] * (self.rows * self.cols)
            self.is_finished = False
            self.winning_line = None
            self.winner = None
            self.last_move = None
            p_ids = list(self.players.keys())
            if len(p_ids) >= 2:
                if self.first_turn_rule == "random":
                    self.current_turn = random.choice(p_ids)
                elif self.first_turn_rule == "guest":
                    self.current_turn = p_ids[1]
                else:
                    self.current_turn = p_ids[0]

                if self.current_turn == "bot_tanjun":
                    bot_col = self._bot_calculate_move()
                    if bot_col != -1:
                        bot_row = self._get_lowest_empty_row(bot_col)
                        if bot_row != -1:
                            bot_idx = bot_row * self.cols + bot_col
                            self.board[bot_idx] = self.player_symbols.get("bot_tanjun", "Y")
                            self.last_move = bot_idx
                            self.current_turn = p_ids[0] if p_ids[1] == "bot_tanjun" else p_ids[1]
            return {"status": "restarted", "state": self.get_state()}

        if action == "lobby":
            self.board = [""] * (self.rows * self.cols)
            self.is_started = False
            self.is_finished = False
            self.winner = None
            self.winning_line = None
            self.last_move = None
            if "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None
            return {"status": "lobby", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.board = [""] * (self.rows * self.cols)
        self.is_started = False
        self.is_finished = False
        self.winner = None
        self.winning_line = None
        self.last_move = None
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
            "rows": self.rows,
            "cols": self.cols,
            "last_move": self.last_move,
            "connect_target": self.connect_target,
            "first_turn": self.first_turn_rule,
            "current_turn": self.current_turn,
            "player_symbols": self.player_symbols,
            "scores": self.scores,
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
