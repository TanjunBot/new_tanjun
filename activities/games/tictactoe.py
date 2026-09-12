from __future__ import annotations

import asyncio
import random
from typing import Any, Dict, List, Optional
from activities.base import BaseGame, Player, serialized_action


class TicTacToeGame(BaseGame):
    """Tic Tac Toe implementation supporting 2-player multiplayer & Tanjun Bot AI."""

    def __init__(self, session_id: str, host: Player, difficulty: int = 3) -> None:
        super().__init__(session_id=session_id, host=host, max_players=2)
        self.board: List[str] = [""] * 9
        self.difficulty: int = difficulty  # 1 (easy) to 5 (unbeatable)
        self.first_turn_rule: str = "host"
        self.current_turn: Optional[str] = None  # player user_id
        self.player_symbols: Dict[str, str] = {}  # user_id -> "X" or "O"
        self.winning_line: Optional[List[int]] = None
        self.scores: Dict[str, int] = {}
        self.bot_player: Optional[Player] = None
        self.last_move: Optional[int] = None

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

    def start_game(self) -> bool:
        p_ids = list(self.players.keys())
        if len(p_ids) == 1 and self.game_mode == "bot":
            self.setup_bot(self.difficulty)
            p_ids = list(self.players.keys())

        if len(p_ids) < 2:
            return False

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

        # Decide first turn
        if self.first_turn_rule == "random":
            self.current_turn = random.choice(p_ids)
        elif self.first_turn_rule == "guest" and len(p_ids) > 1:
            self.current_turn = p_ids[1]
        else:
            self.current_turn = p_ids[0]

        # If bot plays first, bot makes move
        if self.current_turn == "bot_tanjun":
            bot_move = self._bot_calculate_move()
            if bot_move != -1:
                self.board[bot_move] = self.player_symbols.get("bot_tanjun", "O")
                self.last_move = bot_move
                self.current_turn = p_ids[1] if p_ids[0] == "bot_tanjun" else p_ids[0]

        return True

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
                diff = int(data.get("difficulty", 3))
            except (TypeError, ValueError):
                return {"error": "Invalid difficulty"}
            first_turn = data.get("first_turn", "host")
            if first_turn not in {"host", "guest", "random"}:
                return {"error": "Invalid first turn"}
            self.difficulty = max(1, min(5, diff))
            self.first_turn_rule = first_turn
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
                return {"status": "error", "error": "Game is not active"}
            if player_id not in self.players or player_id in self.spectators:
                return {"status": "error", "error": "Spectators cannot make moves"}
            if self.current_turn != player_id:
                return {"status": "error", "error": "Not your turn"}

            cell = data.get("cell")
            if cell is None or isinstance(cell, bool) or not isinstance(cell, int) or not (0 <= cell <= 8) or self.board[cell] != "":
                return {"status": "error", "error": "Invalid cell move"}

            sym = self.player_symbols.get(player_id)
            if not sym:
                return {"status": "error", "error": "Unknown player symbol"}
            self.board[cell] = sym
            self.last_move = cell

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
                if len(p_ids) < 2:
                    self.is_finished = True
                    self.winner = player_id
                    return {"status": "moved", "state": self.get_state()}
                next_player = p_ids[1] if self.current_turn == p_ids[0] else p_ids[0]
                self.current_turn = next_player

                # If next player is bot, schedule/execute bot move
                if next_player == "bot_tanjun" and not self.is_finished:
                    if broadcast_cb:
                        await broadcast_cb()
                    await asyncio.sleep(0.55)  # Natural thinking pause
                    bot_move = self._bot_calculate_move()
                    if bot_move != -1:
                        bot_sym = self.player_symbols.get("bot_tanjun", "O")
                        self.board[bot_move] = bot_sym
                        self.last_move = bot_move
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
            if not self.is_controller(player_id):
                return {"error": "Only the host can restart the game"}
            self.board = [""] * 9
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
                    bot_move = self._bot_calculate_move()
                    if bot_move != -1:
                        bot_sym = self.player_symbols.get("bot_tanjun", "O")
                        self.board[bot_move] = bot_sym
                        self.last_move = bot_move
                        self.current_turn = p_ids[0] if p_ids[1] == "bot_tanjun" else p_ids[1]
            return {"status": "restarted", "state": self.get_state()}

        if action == "lobby":
            if not self.is_controller(player_id):
                return {"error": "Only the host can return to the lobby"}
            self.board = [""] * 9
            self.is_started = False
            self.is_finished = False
            self.winner = None
            self.winning_line = None
            self.last_move = None
            if "bot_tanjun" in self.players:
                del self.players["bot_tanjun"]
                self.bot_player = None
            self.scores = {pid: 0 for pid in self.players}
            return {"status": "lobby", "state": self.get_state()}

        return {"error": f"Unknown action: {action}"}

    async def reset(self) -> None:
        self.board = [""] * 9
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
            "board": list(self.board),
            "last_move": self.last_move,
            "first_turn": self.first_turn_rule,
            "current_turn": self.current_turn,
            "player_symbols": dict(self.player_symbols),
            "scores": dict(self.scores),
            "players": [p.model_dump() for p in self.players.values()],
            "spectators": [p.model_dump() for p in self.spectators.values()]
        }
