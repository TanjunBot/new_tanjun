"""
Advanced Tic-Tac-Toe (Ultimate Tic-Tac-Toe)

A 3x3 grid of Tic-Tac-Toe boards. Players play in the board corresponding
to the position of the previous move. When a board is won/complete, the
next player can choose any available board.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Coroutine
from typing import Any

import discord

import utility

EMPTY = "⬜"
PLAYER1_GLOBAL = "❌"
PLAYER2_GLOBAL = "⭕"
PLAYER1_LOCAL = "❌"
PLAYER2_LOCAL = "⭕"


class AdvancedTicTacToe:
    def __init__(self, player1: discord.Member, player2: discord.Member | None = None) -> None:
        self.player1 = player1
        self.player2 = player2 if player2 else "tanjun"
        self.current_player = player1
        self.winner: str | None = None
        self.game_over = False
        self.player1_move = PLAYER1_GLOBAL
        self.player2_move = PLAYER2_GLOBAL
        self.message: discord.Message | None = None

        # 9 boards (0-8), each is a 3x3 grid of cells
        self.boards: list[list[list[str]]] = [
            [[EMPTY for _ in range(3)] for _ in range(3)] for _ in range(9)
        ]

        # Master board: tracks who won each sub-board or "full"/" "
        self.master_board: list[str] = [EMPTY for _ in range(9)]

        # The board that must be played in next (0-8). -1 means free choice.
        self.next_board: int = -1

        # For bot difficulty
        self.bot_difficulty = random.randint(1, 5)

    def check_local_winner(self, board_idx: int) -> str | None:
        """Check if sub-board board_idx has a winner. Returns player symbol or None."""
        board = self.boards[board_idx]
        # Rows
        for r in range(3):
            if board[r][0] == board[r][1] == board[r][2] != EMPTY:
                return board[r][0]
        # Columns
        for c in range(3):
            if board[0][c] == board[1][c] == board[2][c] != EMPTY:
                return board[0][c]
        # Diagonals
        if board[0][0] == board[1][1] == board[2][2] != EMPTY:
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != EMPTY:
            return board[0][2]
        return None

    def is_local_full(self, board_idx: int) -> bool:
        """Check if sub-board board_idx is full (no empty cells)."""
        for row in self.boards[board_idx]:
            for cell in row:
                if cell == EMPTY:
                    return False
        return True

    def check_global_winner(self) -> str | None:
        """Check if there is a winner on the master board."""
        mb = self.master_board
        # Rows
        for r in range(3):
            if mb[r * 3] == mb[r * 3 + 1] == mb[r * 3 + 2] not in (EMPTY, "full"):
                return mb[r * 3]
        # Columns
        for c in range(3):
            if mb[c] == mb[c + 3] == mb[c + 6] not in (EMPTY, "full"):
                return mb[c]
        # Diagonals
        if mb[0] == mb[4] == mb[8] not in (EMPTY, "full"):
            return mb[0]
        if mb[2] == mb[4] == mb[6] not in (EMPTY, "full"):
            return mb[2]
        return None

    def is_global_full(self) -> bool:
        """Check if all sub-boards are decided."""
        return all(cell != EMPTY for cell in self.master_board)

    def get_available_local_moves(self, board_idx: int) -> list[tuple[int, int]]:
        """Get available (row, col) moves within a sub-board."""
        moves: list[tuple[int, int]] = []
        board = self.boards[board_idx]
        for r in range(3):
            for c in range(3):
                if board[r][c] == EMPTY:
                    moves.append((r, c))
        return moves

    def get_playable_boards(self) -> list[int]:
        """Get list of board indices that can be played in."""
        if self.next_board != -1:
            # If the targeted board is still playable, return it
            if self.master_board[self.next_board] == EMPTY:
                return [self.next_board]
            # Otherwise, free choice
            return [i for i in range(9) if self.master_board[i] == EMPTY]
        # Free choice: all boards not yet decided
        return [i for i in range(9) if self.master_board[i] == EMPTY]

    def make_move(self, board_idx: int, row: int, col: int) -> bool:
        """Make a move. Returns True if valid and made."""
        if self.game_over or self.winner:
            return False

        # Check board is playable
        playable = self.get_playable_boards()
        if board_idx not in playable:
            return False

        # Check cell is empty
        if self.boards[board_idx][row][col] != EMPTY:
            return False

        # Place symbol
        symbol = self.player1_move if self.current_player == self.player1 else self.player2_move
        self.boards[board_idx][row][col] = symbol

        # Check if this sub-board is won
        local_winner = self.check_local_winner(board_idx)
        if local_winner:
            self.master_board[board_idx] = symbol
        elif self.is_local_full(board_idx):
            self.master_board[board_idx] = "full"

        # Check global winner
        self.winner = self.check_global_winner()
        if self.winner or self.is_global_full():
            self.game_over = True

        # Set next board based on where the player sent the game
        next_idx = row * 3 + col
        if not self.game_over:
            self.next_board = next_idx
            # If that board is already decided, allow free choice
            if self.master_board[next_idx] != EMPTY and not self.is_global_full():
                self.next_board = -1

        # Toggle turn
        if self.player2 == "tanjun" or getattr(self.player2, "bot", False):
            # In bot mode, this will be toggled after bot move
            pass
        else:
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1

        return True

    def _bot_minimax_evaluate(self) -> int:
        """Simple evaluation for bot move selection."""
        # If global winner check
        g_winner = self.check_global_winner()
        if g_winner == self.player2_move:
            return 100
        if g_winner == self.player1_move:
            return -100
        return 0

    def _bot_pick_move(self) -> tuple[int, int, int] | None:
        """Bot picks a (board_idx, row, col) move. Simple heuristic."""
        playable = self.get_playable_boards()
        if not playable:
            return None

        # Prefer winning local boards
        for board_idx in playable:
            for r in range(3):
                for c in range(3):
                    if self.boards[board_idx][r][c] == EMPTY:
                        # Try move
                        self.boards[board_idx][r][c] = self.player2_move
                        if self.check_local_winner(board_idx):
                            self.boards[board_idx][r][c] = EMPTY
                            return (board_idx, r, c)
                        self.boards[board_idx][r][c] = EMPTY

        # Block opponent from winning local boards
        for board_idx in playable:
            for r in range(3):
                for c in range(3):
                    if self.boards[board_idx][r][c] == EMPTY:
                        self.boards[board_idx][r][c] = self.player1_move
                        if self.check_local_winner(board_idx):
                            self.boards[board_idx][r][c] = EMPTY
                            return (board_idx, r, c)
                        self.boards[board_idx][r][c] = EMPTY

        # Prefer center board (index 4) and center cells
        # Try to take center of master: board 4
        center_prefs = [4, 0, 2, 6, 8, 1, 3, 5, 7]
        for board_idx in center_prefs:
            if board_idx in playable:
                # Center cell
                if self.boards[board_idx][1][1] == EMPTY:
                    return (board_idx, 1, 1)
                # Corners
                for cr, cc in [(0, 0), (0, 2), (2, 0), (2, 2)]:
                    if self.boards[board_idx][cr][cc] == EMPTY:
                        return (board_idx, cr, cc)
                # Edges
                for er, ec in [(0, 1), (1, 0), (1, 2), (2, 1)]:
                    if self.boards[board_idx][er][ec] == EMPTY:
                        return (board_idx, er, ec)

        # Random fallback
        board_idx = random.choice(playable)
        moves = self.get_available_local_moves(board_idx)
        if moves:
            r, c = random.choice(moves)
            return (board_idx, r, c)
        return None

    def _bot_move(self) -> None:
        """Execute the bot's move."""
        move = self._bot_pick_move()
        if move:
            board_idx, row, col = move
            self.make_move(board_idx, row, col)
            self.current_player = self.player1

    def _get_emoji_for_cell(self, cell: str) -> str:
        """Map cell value to display emoji."""
        mapping = {
            EMPTY: "⬜",
            "❌": "❌",
            "⭕": "⭕",
        }
        return mapping.get(cell, "⬜")

    def _get_button_style(self, cell: str) -> discord.ButtonStyle:
        if cell == "❌":
            return discord.ButtonStyle.danger
        if cell == "⭕":
            return discord.ButtonStyle.success
        return discord.ButtonStyle.secondary

    def _get_master_emoji(self, cell: str) -> str:
        mapping = {
            EMPTY: "⬜",
            "❌": "❌",
            "⭕": "⭕",
            "full": "🔲",
        }
        return mapping.get(cell, "⬜")

    def build_embed(self, interaction: discord.Interaction) -> discord.Embed:
        """Build the game embed."""
        title = "Advanced Tic-Tac-Toe"
        lines: list[str] = []

        # Master board indicator
        mb_line = "Master Board: "
        for i in range(9):
            mb_line += self._get_master_emoji(self.master_board[i])
        lines.append(mb_line)
        lines.append("")

        # Build the visual grid — 9 sub-boards in 3x3 layout
        # Each sub-board is displayed as compact text
        for board_row in range(3):
            row_lines: list[str] = ["", "", ""]
            for board_col in range(3):
                board_idx = board_row * 3 + board_col
                board = self.boards[board_idx]
                for r in range(3):
                    for c in range(3):
                        cell = board[r][c]
                        if cell == "❌":
                            row_lines[r] += "❌"
                        elif cell == "⭕":
                            row_lines[r] += "⭕"
                        else:
                            row_lines[r] += "⬜"
                    row_lines[r] += "  " if board_col < 2 else ""
            for line in row_lines:
                lines.append(line)
            lines.append("")  # separator between master rows

        # Game info
        p2_name = self.player2.mention if self.player2 != "tanjun" else "Tanjun"
        lines.append(f"**{self.player1.mention}** ({PLAYER1_GLOBAL}) vs **{p2_name}** ({PLAYER2_GLOBAL})")

        if self.game_over:
            if self.winner:
                winner_name = (
                    self.player1.mention if self.winner == self.player1_move else p2_name
                )
                lines.append(f"\n🏆 **{winner_name} wins!** 🏆")
            else:
                lines.append("\n🤝 **It's a draw!** 🤝")
        else:
            turn_name = self.current_player.mention if self.current_player != "tanjun" else "Tanjun"
            lines.append(f"\n**Turn:** {turn_name}")

            if self.next_board != -1:
                lines.append(f"Play in board **{self.next_board + 1}**")
            else:
                lines.append("Play in **any** available board!")
            if self.player2 == "tanjun":
                lines.append(f"Bot difficulty: {self.bot_difficulty}/5")

        embed = utility.tanjunEmbed(
            title=title,
            description="\n".join(lines),
        )
        return embed

    async def update_board(
        self,
        interaction: discord.Interaction,
        initial: bool = False,
        timeout: bool = False,
    ) -> None:
        embed = self.build_embed(interaction)
        view = self.get_view(timeout=3600, disable_on_timeout=timeout)
        if initial:
            self.message = await interaction.followup.send(embed=embed, view=view)
        elif interaction.message:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                embed=embed,
                view=view,
            )

    def get_view(
        self,
        timeout: int = 3600,
        disable_on_timeout: bool = True,
    ) -> discord.ui.View:
        game = self  # capture for closure

        class AdvancedTTTView(discord.ui.View):
            def __init__(self) -> None:
                super().__init__(timeout=timeout)
                self.game = game
                self._build_buttons()

            async def on_timeout(self) -> None:
                for child in self.children:
                    child.disabled = True  # type: ignore[attr-defined]
                if game.message:
                    await game.message.edit(view=self)

            def _build_buttons(self) -> None:
                """Create 81 buttons: 9 boards x 3x3 cells."""
                playable_boards = game.get_playable_boards()
                for board_idx in range(9):
                    board = game.boards[board_idx]
                    is_board_playable = board_idx in playable_boards
                    for r in range(3):
                        for c in range(3):
                            cell = board[r][c]
                            is_cell_empty = cell == EMPTY
                            disabled = game.game_over or not is_board_playable or not is_cell_empty
                            style = game._get_button_style(cell)
                            custom_id = f"advttt_{board_idx}_{r}_{c}"

                            # Each grid of 9 buttons is in a section of 3 rows
                            # Board layout: boards 0-2 on row 0-2, boards 3-5 on row 3-5, boards 6-8 on row 6-8
                            # Within a board, rows r=0,1,2 map to button rows
                            # board_row 0 contains boards 0,1,2 -> button rows 0,1,2
                            # board_row 1 contains boards 3,4,5 -> button rows 3,4,5
                            # board_row 2 contains boards 6,7,8 -> button rows 6,7,8
                            board_row_in_group = board_idx // 3  # 0, 1, 2
                            actual_row = board_row_in_group * 3 + r  # 0-8

                            # Columns: boards within a row group
                            # board 0 -> cols 0,1,2; board 1 -> cols 3,4,5; board 2 -> cols 6,7,8

                            btn = discord.ui.Button(
                                label=game._get_emoji_for_cell(cell),
                                style=style,
                                disabled=disabled,
                                row=actual_row,
                                custom_id=custom_id,
                            )
                            btn.callback = self._make_callback(board_idx, r, c)  # type: ignore[method-assign]
                            self.add_item(btn)

            def _make_callback(
                self, board_idx: int, row: int, col: int
            ) -> Callable[[discord.Interaction], Coroutine[Any, Any, None]]:
                async def callback(interaction: discord.Interaction) -> None:
                    await self.handle_move(interaction, board_idx, row, col)
                return callback

            async def handle_move(
                self,
                interaction: discord.Interaction,
                board_idx: int,
                row: int,
                col: int,
            ) -> None:
                await interaction.response.defer()

                p2_id = game.player2.id if game.player2 != "tanjun" else None
                if interaction.user.id not in [game.player1.id, p2_id] and p2_id is not None:
                    await interaction.followup.send(
                        "This is not your game!",
                        ephemeral=True,
                    )
                    return

                if interaction.user != game.current_player and game.current_player != "tanjun":
                    await interaction.followup.send(
                        "It's not your turn!",
                        ephemeral=True,
                    )
                    return

                if game.game_over:
                    await interaction.followup.send(
                        "The game is already over!",
                        ephemeral=True,
                    )
                    return

                if not game.make_move(board_idx, row, col):
                    await interaction.followup.send(
                        "Invalid move. Try again!",
                        ephemeral=True,
                    )
                    return

                # If playing vs bot, do bot move
                if not game.game_over and (game.player2 == "tanjun" or getattr(game.player2, "bot", False)):
                    game._bot_move()

                await game.update_board(interaction)

        return AdvancedTTTView()


async def advanced_tic_tac_toe(
    command_info: utility.CommandInfo,
    player1: discord.Member,
    player2: discord.Member | None = None,
) -> None:
    game = AdvancedTicTacToe(player1, player2)
    await game.update_board(command_info, initial=True)  # type: ignore[arg-type]
