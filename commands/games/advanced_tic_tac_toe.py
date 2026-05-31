"""Advanced Tic-Tac-Toe (Ultimate Tic-Tac-Toe).

A 9x9 meta-board consisting of 9 smaller 3x3 boards.
The goal is to win the "master game" by winning sub-boards.
The player's move position within a sub-board determines which
sub-board the opponent must play in next.
"""

import random

import discord

import utility


class AdvancedTicTacToe:
    """Ultimate Tic-Tac-Toe with 9 sub-boards on a meta 3x3 grid."""

    def __init__(self, player1: discord.Member, player2: discord.Member | None = None) -> None:
        self.player1 = player1
        self.player2 = player2 or "tanjun"
        # boards[meta_row][meta_col] is a 3x3 list of sub-board cells
        self.boards: list[list[list[list[str]]]] = [
            [  # meta_row
                [  # meta_col
                    ["-"] * 3  # row of sub-board
                    for _ in range(3)
                ]
                for _ in range(3)
            ]
            for _ in range(3)
        ]
        # Track winners of each sub-board: None = ongoing, "⭕" or "❌" or "D" (draw)
        self.board_winners: list[list[str | None]] = [[None] * 3 for _ in range(3)]
        # Which sub-board the next player MUST play in (None = free choice)
        self.next_board: tuple[int, int] | None = None
        self.current_player: discord.Member | str = player1
        self.winner: str | None = None
        self.game_over = False
        self.player1_move = "⭕"
        self.player2_move = "❌"
        self.bot_difficulty = random.randint(1, 5)
        self.message: discord.Message | None = None

    # --- Win / draw detection ---

    def check_board_winner(self, board: list[list[str]]) -> str | None:
        """Check a single 3x3 sub-board for a winner. Returns symbol or None."""
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] and board[i][0] != "-":
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] and board[0][i] != "-":
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] and board[0][0] != "-":
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] and board[0][2] != "-":
            return board[0][2]
        return None

    def is_board_full(self, board: list[list[str]]) -> bool:
        return all(cell != "-" for row in board for cell in row)

    def check_meta_winner(self) -> str | None:
        """Check the 3x3 meta-board (board_winners) for a winner."""
        bw = self.board_winners
        for i in range(3):
            if bw[i][0] is not None and bw[i][0] == bw[i][1] == bw[i][2] and bw[i][0] not in ("-", "D"):
                return bw[i][0]
            if bw[0][i] is not None and bw[0][i] == bw[1][i] == bw[2][i] and bw[0][i] not in ("-", "D"):
                return bw[0][i]
        if bw[0][0] is not None and bw[0][0] == bw[1][1] == bw[2][2] and bw[0][0] not in ("-", "D"):
            return bw[0][0]
        if bw[0][2] is not None and bw[0][2] == bw[1][1] == bw[2][0] and bw[0][2] not in ("-", "D"):
            return bw[0][2]
        return None

    def is_meta_full(self) -> bool:
        return all(bw is not None for row in self.board_winners for bw in row)

    def update_board_winner(self, mr: int, mc: int) -> None:
        """Check and update the winner/draw status of sub-board (mr, mc)."""
        if self.board_winners[mr][mc] is not None:
            return
        board = self.boards[mr][mc]
        w = self.check_board_winner(board)
        if w is not None:
            self.board_winners[mr][mc] = w
        elif self.is_board_full(board):
            self.board_winners[mr][mc] = "D"

    # --- Move logic ---

    def make_move(self, mr: int, mc: int, sr: int, sc: int) -> bool:
        """Place the current player's symbol. Returns True if valid."""
        # Validate the move is in the correct sub-board if next_board is set
        if self.next_board is not None and (mr, mc) != self.next_board:
            return False
        if self.board_winners[mr][mc] is not None:
            return False
        board = self.boards[mr][mc]
        if board[sr][sc] != "-":
            return False
        symbol = self.player1_move if self.current_player == self.player1 else self.player2_move
        board[sr][sc] = symbol

        # Check if this sub-board is now won/drawn
        self.update_board_winner(mr, mc)

        # Determine next forced sub-board — the position (sr, sc) in THIS sub-board
        # determines WHICH sub-board the opponent must play in
        self.next_board = (sr, sc)
        # But if that sub-board is already finished, the next player is free
        if self.board_winners[sr][sc] is not None:
            self.next_board = None
        # Also check if all sub-boards in the forced direction are finished
        # (player can play anywhere)

        # Check meta winner
        meta_winner = self.check_meta_winner()
        if meta_winner:
            self.winner = meta_winner
            self.game_over = True
        elif self.is_meta_full():
            self.game_over = True

        # Switch turn
        self.toggle_turn()
        return True

    def toggle_turn(self) -> None:
        if self.player2 == "tanjun" or (hasattr(self.player2, "bot") and self.player2.bot):
            self.current_player = self.player1
        else:
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def get_valid_moves(self) -> list[tuple[int, int, int, int]]:
        """Return list of (meta_row, meta_col, sub_row, sub_col) valid moves."""
        moves: list[tuple[int, int, int, int]] = []
        # Determine which meta-boards to consider
        boards_to_check: list[tuple[int, int]] = []
        if self.next_board is not None and self.board_winners[self.next_board[0]][self.next_board[1]] is None:
            boards_to_check = [self.next_board]
        else:
            # Free choice: pick all unfinished boards
            for mr in range(3):
                for mc in range(3):
                    if self.board_winners[mr][mc] is None:
                        boards_to_check.append((mr, mc))

        for mr, mc in boards_to_check:
            board = self.boards[mr][mc]
            for sr in range(3):
                for sc in range(3):
                    if board[sr][sc] == "-":
                        moves.append((mr, mc, sr, sc))
        return moves

    # --- Bot AI ---

    def bot_move(self) -> tuple[int, int, int, int] | None:
        """Pick a move for the bot using minimax on the sub-boards."""
        moves = self.get_valid_moves()
        if not moves:
            return None

        # Simple bot: if difficulty is low, pick randomly
        if self.bot_difficulty <= 2:
            return random.choice(moves)

        # Medium: prefer winning a sub-board or blocking opponent
        if self.bot_difficulty <= 3:
            # Try to find a winning move
            winning_moves: list[tuple[int, int, int, int]] = []
            blocking_moves: list[tuple[int, int, int, int]] = []
            for m in moves:
                mr, mc, sr, sc = m
                # Simulate bot move
                self.boards[mr][mc][sr][sc] = self.player2_move
                w = self.check_board_winner(self.boards[mr][mc])
                self.boards[mr][mc][sr][sc] = "-"
                if w == self.player2_move:
                    winning_moves.append(m)
                # Simulate player move (blocking)
                self.boards[mr][mc][sr][sc] = self.player1_move
                w2 = self.check_board_winner(self.boards[mr][mc])
                self.boards[mr][mc][sr][sc] = "-"
                if w2 == self.player1_move:
                    blocking_moves.append(m)
            if winning_moves:
                return random.choice(winning_moves)
            if blocking_moves:
                return random.choice(blocking_moves)
            return random.choice(moves)

        # Higher difficulty: also consider meta-game implications
        # (prefer moves that send opponent to a finished board, etc.)
        best_moves: list[tuple[int, int, int, int]] = []
        best_score = float("-inf")
        for m in moves:
            mr, mc, sr, sc = m
            score = 0
            # Winning a sub-board is good
            self.boards[mr][mc][sr][sc] = self.player2_move
            w = self.check_board_winner(self.boards[mr][mc])
            self.boards[mr][mc][sr][sc] = "-"
            if w == self.player2_move:
                score += 50
            # Sending opponent to an already-won board is great
            if self.board_winners[sr][sc] is not None:
                score += 20
            # Sending opponent to a board where we already have more pieces
            opp_board = self.boards[sr][sc]
            if self.board_winners[sr][sc] is None and not self.is_board_full(opp_board):
                our_count = sum(row.count(self.player2_move) for row in opp_board)
                opp_count = sum(row.count(self.player1_move) for row in opp_board)
                score += our_count - opp_count
            # Center of meta-board is strategic
            if mr == 1 and mc == 1:
                score += 3
            if score > best_score:
                best_score = score
                best_moves = [m]
            elif score == best_score:
                best_moves.append(m)
        return random.choice(best_moves) if best_moves else random.choice(moves)

    # --- Discord UI ---

    async def update_board(
        self,
        interaction: discord.Interaction,
        initial: bool = False,
        timeout: bool = False,
    ) -> None:
        title = "Advanced Tic-Tac-Toe"
        description = (
            f"**{self.player1.mention}** ({self.player1_move}) vs "
            f"**{self.player2.mention if self.player2 != 'tanjun' else 'Tanjun'}** ({self.player2_move})\n\n"
        )

        if self.game_over:
            if self.winner:
                winner_name = (
                    self.player1.mention
                    if self.winner == self.player1_move
                    else (self.player2.mention if self.player2 != "tanjun" else "Tanjun")
                )
                description += f"🏆 **{winner_name} wins the game!** 🏆"
            else:
                description += "🤝 **It's a draw!** 🤝"
        else:
            target = ""
            if self.next_board is not None:
                target = f"Play in board **({self.next_board[0] + 1}, {self.next_board[1] + 1})**."
            else:
                target = "Play in any unfinished board."
            current = self.current_player.mention if self.current_player != "tanjun" else "Tanjun"
            description += f"**{current}**'s turn. {target}"

        embed = utility.tanjunEmbed(title=title, description=description)
        view = self.get_board_view(timeout=3600, disable_on_timeout=timeout)
        if initial:
            self.message = await interaction.reply(embed=embed, view=view)  # type: ignore[attr-defined]
        else:
            await interaction.followup.edit_message(
                message_id=interaction.message.id,
                view=view,
                embed=embed,
            )

    def get_board_view(self, timeout: int = 3600, disable_on_timeout: bool = True) -> discord.ui.View:
        """Build the full interactive view with 9 sub-board panels."""
        view = discord.ui.View(timeout=timeout)
        view._game = self  # type: ignore[attr-defined]

        # Create 9 sub-board panels, each labeled by their meta position
        for mr in range(3):
            for mc in range(3):
                sub_board_won = self.board_winners[mr][mc]
                disabled = sub_board_won is not None or self.game_over
                if not disabled and self.next_board is not None and (mr, mc) != self.next_board:
                    disabled = True

                label = self._render_mini_board(mr, mc, sub_board_won)
                custom_id = f"a{random.randint(0, 2**31 - 1)}"

                # We need 3 rows of 3 sub-boards
                row = mr

                # Build button for this sub-board that opens a modal or sends a followup
                button = discord.ui.Button(
                    label=label[:80] if len(label) > 80 else label,  # Discord button label limit
                    style=discord.ButtonStyle.secondary,
                    disabled=disabled,
                    row=row,
                    custom_id=custom_id,
                )

                async def button_callback(
                    i: discord.Interaction,
                    _mr: int = mr,
                    _mc: int = mc,
                ) -> None:
                    if self.game_over:
                        await i.response.send_message("Game is over.", ephemeral=True)
                        return
                    # Compute allowed participant IDs
                    allowed_ids = {self.player1.id}
                    if isinstance(self.player2, discord.Member):
                        allowed_ids.add(self.player2.id)
                    if i.user.id not in allowed_ids:
                        await i.response.send_message("This is not your game!", ephemeral=True)
                        return
                    if i.user != self.current_player and self.current_player != "tanjun":
                        await i.response.send_message("It's not your turn!", ephemeral=True)
                        return

                    # Check if this sub-board is playable
                    if self.board_winners[_mr][_mc] is not None:
                        await i.response.send_message("This board is already finished.", ephemeral=True)
                        return
                    if self.next_board is not None and (_mr, _mc) != self.next_board:
                        await i.response.send_message(
                            f"You must play in board ({self.next_board[0] + 1}, {self.next_board[1] + 1})!",
                            ephemeral=True,
                        )
                        return

                    # Show sub-board selection
                    await self._show_sub_board(i, _mr, _mc)

                button.callback = button_callback
                view.add_item(button)

        return view

    def _render_mini_board(self, mr: int, mc: int, winner: str | None) -> str:
        """Render a small text representation of the sub-board."""
        if winner == self.player1_move:
            return "⭕"
        if winner == self.player2_move:
            return "❌"
        if winner == "D":
            return "➖"
        board = self.boards[mr][mc]
        lines = []
        for row in board:
            line = " ".join("⬜" if c == "-" else c for c in row)
            lines.append(line)
        return "\n".join(lines)

    async def _show_sub_board(self, interaction: discord.Interaction, mr: int, mc: int) -> None:
        """Show a 3x3 button grid for the selected sub-board to make a move."""
        if self.board_winners[mr][mc] is not None:
            await interaction.response.send_message("This board is already finished.", ephemeral=True)
            return

        board = self.boards[mr][mc]
        view = discord.ui.View(timeout=120)

        for sr in range(3):
            for sc in range(3):
                cell = board[sr][sc]
                disabled = cell != "-" or self.game_over

                label = "⬜" if cell == "-" else cell
                style = discord.ButtonStyle.secondary if cell == "-" else discord.ButtonStyle.gray
                custom_id = f"sm{mr}{mc}{sr}{sc}"

                button = discord.ui.Button(
                    label=label,
                    style=style,
                    disabled=disabled,
                    row=sr,
                    custom_id=custom_id,
                )

                async def cell_callback(
                    i: discord.Interaction,
                    _mr: int = mr,
                    _mc: int = mc,
                    _sr: int = sr,
                    _sc: int = sc,
                ) -> None:
                    await i.response.defer()
                    if self.game_over:
                        return
                    valid = self.make_move(_mr, _mc, _sr, _sc)
                    if not valid:
                        await i.followup.send("Invalid move!", ephemeral=True)
                        return

                    # Update the full game view
                    await self.update_board(i)

                    # If game is not over and opponent is bot, make bot move
                    if not self.game_over and (
                        self.player2 == "tanjun"
                        or (
                            hasattr(self.player2, "bot") and self.player2.bot
                        )
                    ):
                        bot_m = self.bot_move()
                        if bot_m:
                            self.make_move(*bot_m)
                            await self.update_board(i)

                button.callback = cell_callback
                view.add_item(button)

        # Cancel button to go back
        cancel = discord.ui.Button(
            label="↩ Back",
            style=discord.ButtonStyle.danger,
            row=3,
            custom_id=f"cancel{mr}{mc}",
        )

        async def cancel_callback(i: discord.Interaction) -> None:
            await i.response.defer()
            await self.update_board(i)

        cancel.callback = cancel_callback
        view.add_item(cancel)

        embed = discord.Embed(
            title=f"Board ({mr + 1}, {mc + 1})",
            description="Choose your cell:",
            color=discord.Color.blue(),
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def advanced_tic_tac_toe(
    command_info: utility.CommandInfo,
    player1: discord.Member,
    player2: discord.Member | None = None,
) -> None:
    if player2 is None:
        player2 = "tanjun"

    game = AdvancedTicTacToe(player1, player2)
    await game.update_board(command_info, initial=True)
