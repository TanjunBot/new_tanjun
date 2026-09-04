from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional
from activities.base import BaseGame, Player


class TicTacToeGame(BaseGame):
    """Tic Tac Toe implementation supporting 2-player multiplayer & Tanjun Bot AI."""

    def __init__(self, session_id: str, host: Player, difficulty: int = 3) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.board: List[str] = [""] * 9
        self.difficulty: int = difficulty  # 1 (easy) to 5 (unbeatable)
        self.current_turn: Optional[str] = None  # player user_id
        self.player_symbols: Dict[str, str] = {}  # user_id -> "X" or "O"
        self.winning_line: Optional[List[int]] = None
        self.scores: Dict[str, int] = {}
        self.bot_player: Optional[Player] = None

    @property
    def game_type(self) -> str:
        return "tictactoe"

    @property
    def display_name(self) -> str:
        return "Tic-Tac-Toe"

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

    def start_game(self) -> None:
        p_ids = list(self.players.keys())
        if len(p_ids) == 1 and self.game_mode == "bot":
            self.setup_bot(self.difficulty)
            p_ids = list(self.players.keys())

        if len(p_ids) < 2:
            return

        self.board = [""] * 9
        self.is_started = True
        self.is_finished = False
        self.winner = None
        self.winning_line = None

        # Assign X and O
        self.player_symbols = {
            p_ids[0]: "X",
            p_ids[1]: "O"
        }
        for pid in p_ids:
            if pid not in self.scores:
                self.scores[pid] = 0

        # X always starts
        self.current_turn = p_ids[0]

    def check_winner(self, b: Optional[List[str]] = None) -> tuple[Optional[str], Optional[List[int]]]:
        board = b or self.board
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        for line in lines:
            if board[line[0]] and board[line[0]] == board[line[1]] == board[line[2]]:
                return board[line[0]], line

        if all(cell != "" for cell in board):
            return "draw", None

        return None, None

    def _minimax(self, b: List[str], depth: int, is_max: bool, bot_sym: str, human_sym: str) -> int:
        winner, _ = self.check_winner(b)
        if winner == bot_sym:
            return 10 - depth
        if winner == human_sym:
            return depth - 10
        if winner == "draw":
            return 0
        if depth >= 6:
            return 0

        if is_max:
            best = -1000
            for i in range(9):
                if b[i] == "":
                    b[i] = bot_sym
                    best = max(best, self._minimax(b, depth + 1, False, bot_sym, human_sym))
                    b[i] = ""
            return best
        else:
            best = 1000
            for i in range(9):
                if b[i] == "":
                    b[i] = human_sym
                    best = min(best, self._minimax(b, depth + 1, True, bot_sym, human_sym))
                    b[i] = ""
            return best

    def _bot_calculate_move(self) -> int:
        empty_indices = [i for i, x in enumerate(self.board) if x == ""]
        if not empty_indices:
            return -1

        # Difficulty check: chance to play randomly
        # diff 1: 80% random, diff 2: 50% random, diff 3: 25% random, diff 4: 10% random, diff 5: 0% random (perfect)
        random_chance = {1: 0.8, 2: 0.5, 3: 0.25, 4: 0.1, 5: 0.0}.get(self.difficulty, 0.2)
        if random.random() < random_chance:
            return random.choice(empty_indices)

        bot_sym = self.player_symbols.get("bot_tanjun", "O")
        human_sym = "X" if bot_sym == "O" else "O"

        # Try to win or block immediately if level >= 2
        for move in empty_indices:
            self.board[move] = bot_sym
            w, _ = self.check_winner()
            self.board[move] = ""
            if w == bot_sym:
                return move

        for move in empty_indices:
            self.board[move] = human_sym
            w, _ = self.check_winner()
            self.board[move] = ""
            if w == human_sym:
                return move

        # If center is open, prefer center
        if 4 in empty_indices and random.random() < 0.7:
            return 4

        # Otherwise full minimax
        best_val = -1000
        best_move = empty_indices[0]
        for move in empty_indices:
            self.board[move] = bot_sym
            val = self._minimax(self.board, 0, False, bot_sym, human_sym)
            self.board[move] = ""
            if val > best_val:
                best_val = val
                best_move = move
        return best_move

    async def handle_action(self, player_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if action == "start":
            mode = data.get("mode", "pvp")
            self.game_mode = mode
            diff = int(data.get("difficulty", 3))
            self.difficulty = diff
            if mode == "bot":
                self.setup_bot(diff)
            self.start_game()
            return {"status": "started", "state": self.get_state()}

        if action == "move":
            if not self.is_started or self.is_finished:
                return {"error": "Game is not active"}
            if self.current_turn != player_id:
                return {"error": "Not your turn"}

            cell = data.get("cell")
            if cell is None or not (0 <= cell <= 8) or self.board[cell] != "":
                return {"error": "Invalid cell move"}

            sym = self.player_symbols[player_id]
            self.board[cell] = sym

            # Check winner
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
                # Toggle turn
                p_ids = list(self.players.keys())
                next_player = p_ids[1] if self.current_turn == p_ids[0] else p_ids[0]
                self.current_turn = next_player

                # If next player is bot, schedule/execute bot move
                if next_player == "bot_tanjun" and not self.is_finished:
                    await asyncio.sleep(0.4)  # Natural thinking pause
                    bot_move = self._bot_calculate_move()
                    if bot_move != -1:
                        bot_sym = self.player_symbols["bot_tanjun"]
                        self.board[bot_move] = bot_sym
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
            self.board = [""] * 9
            self.is_finished = False
            self.winning_line = None
            self.winner = None
            p_ids = list(self.players.keys())
            # Alternate who starts
            if len(p_ids) >= 2:
                # Swap symbols for fun or keep host as X
                self.current_turn = p_ids[0] if random.random() > 0.5 else p_ids[1]
            return {"status": "restarted", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.board = [""] * 9
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
            "current_turn": self.current_turn,
            "player_symbols": self.player_symbols,
            "scores": self.scores,
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
