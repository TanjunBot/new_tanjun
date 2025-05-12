import random

import discord

import utility
from localizer import tanjunLocalizer


class TicTacToe:
    def __init__(self, player1: discord.Member, player2: discord.Member = None):
        self.player1 = player1
        self.player2 = player2
        if self.player2 is None:
            self.player2 = "tanjun"
        self.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        self.current_player = player1
        self.winner = None
        self.game_over = False
        self.player1_move = "⭕"
        self.player2_move = "❌"
        self.bot_difficulty = random.randint(1, 5)
        self.message = None

    def check_winner(self, board: list[list[str]] = None):
        if not board:
            board = self.board
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

    def is_full(self, board: list[list[str]] = None):
        if not board:
            board = self.board
        for row in board:
            for cell in row:
                if cell == "-":
                    return False
        return True

    def evaluate_board(self, board: list[list[str]]):
        winner = self.check_winner(board)
        if winner == self.player1_move:
            return -1
        elif winner == self.player2_move:
            return 1
        return 0

    def get_available_moves(self, board: list[list[str]]):
        moves = []
        for i in range(9):
            if board[i // 3][i % 3] == "-":
                moves.append(i)
        return moves

    def minimax(
        self,
        current_player: str,
        depth: int,
        board: list[list[str]],
        maximizing_player: bool,
    ):
        # Check terminal states first
        winner = self.check_winner(board)
        if winner:
            # Return higher scores for quicker wins/losses
            if winner == self.player2_move:
                return 10 + depth, ""  # AI win
            else:
                return -10 - depth, ""  # Player win
        if self.is_full(board):
            return 0, ""

        if depth == 0:
            return 0, ""

        scores = []
        moves = []
        current_move = self.player2_move if maximizing_player else self.player1_move

        for move in self.get_available_moves(board):
            new_board = self.minimax_make_move(board, move, current_move)
            score, _ = self.minimax(current_player, depth - 1, new_board, not maximizing_player)
            scores.append(score)
            moves.append(move)

        if maximizing_player:
            best_score = max(scores)
            best_indices = [i for i, score in enumerate(scores) if score == best_score]
            best_move = moves[random.choice(best_indices)]
        else:
            best_score = min(scores)
            best_indices = [i for i, score in enumerate(scores) if score == best_score]
            best_move = moves[random.choice(best_indices)]

        return best_score, best_move

    def minimax_make_move(self, board: list[list[str]], move: int, player: str):
        # Create a copy of the board
        new_board = [row[:] for row in board]

        # The player parameter is now the actual symbol (X or O), not the player object
        new_board[move // 3][move % 3] = player

        return new_board

    async def update_board(
        self,
        interaction: discord.Interaction,
        initial: bool = False,
        timeout: bool = False,
    ):
        self.winner = self.check_winner()
        title = tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.title")
        description = tanjunLocalizer.localize(
            interaction.locale,
            "commands.games.ticTacToe.description",
            player1=self.player1.mention,
            player2=self.player2.mention if self.player2 != "tanjun" else "Tanjun",
        )
        if self.player2 == "tanjun":
            description += "\n" + tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.games.ticTacToe.descriptionBotEnemy",
                difficulty=self.bot_difficulty,
            )
        if self.winner is not None:
            winner = self.player1 if self.winner == self.player1_move else self.player2
            description += "\n" + tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.games.ticTacToe.winner",
                winner=winner.mention if winner != "tanjun" else "Tanjun",
            )
        elif self.is_full():
            description += "\n" + tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.draw")
        else:
            description += "\n" + tanjunLocalizer.localize(
                str(interaction.locale),
                "commands.games.ticTacToe.currentTurn",
                player=(self.current_player.mention if self.current_player != "tanjun" else "Tanjun"),
            )
        embed = utility.tanjunEmbed(title=title, description=description)
        if initial:
            self.message = await interaction.reply(embed=embed)
        view = self.getBoardView(timeout=3600, disable_on_timeout=timeout, message=self.message)
        if initial:
            await self.message.edit(view=view, embed=embed)
        else:
            await interaction.followup.edit_message(message_id=interaction.message.id, view=view, embed=embed)

    def toggle_turn(self):
        if self.player2 == "tanjun" or self.player2.bot:
            self.current_player = self.player1
        else:
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def getBoardView(
        self,
        timeout: int = 3600,
        disable_on_timeout: bool = True,
        message: discord.Message = None,
    ):
        class TicTacToeView(discord.ui.View):
            def __init__(self, ticTacToe: TicTacToe):
                super().__init__(timeout=timeout)
                self.player1 = ticTacToe.player1
                self.player2 = ticTacToe.player2
                self.board = ticTacToe.board
                self.current_player = ticTacToe.current_player
                self.player1_move = ticTacToe.player1_move
                self.player2_move = ticTacToe.player2_move
                self.bot_difficulty = ticTacToe.bot_difficulty
                self.game_over = ticTacToe.game_over
                self.winner = ticTacToe.winner
                self.check_winner = ticTacToe.check_winner
                self.is_full = ticTacToe.is_full
                self.minimax = ticTacToe.minimax
                self.update_board = ticTacToe.update_board
                self.toggle_turn = ticTacToe.toggle_turn

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True

                await message.edit(view=self)

            @discord.ui.button(
                label=self.board[0][0],
                style=discord.ButtonStyle.secondary,
                custom_id="0",
                disabled=self.board[0][0] != "-" or self.winner is not None or disable_on_timeout,
                row=0,
            )
            async def play_0(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[0][1],
                style=discord.ButtonStyle.secondary,
                custom_id="1",
                disabled=self.board[0][1] != "-" or self.winner is not None or disable_on_timeout,
                row=0,
            )
            async def play_1(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[0][2],
                style=discord.ButtonStyle.secondary,
                custom_id="2",
                disabled=self.board[0][2] != "-" or self.winner is not None or disable_on_timeout,
                row=0,
            )
            async def play_2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[1][0],
                style=discord.ButtonStyle.secondary,
                custom_id="3",
                disabled=self.board[1][0] != "-" or self.winner is not None or disable_on_timeout,
                row=1,
            )
            async def play_3(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[1][1],
                style=discord.ButtonStyle.secondary,
                custom_id="4",
                disabled=self.board[1][1] != "-" or self.winner is not None or disable_on_timeout,
                row=1,
            )
            async def play_4(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[1][2],
                style=discord.ButtonStyle.secondary,
                custom_id="5",
                disabled=self.board[1][2] != "-" or self.winner is not None or disable_on_timeout,
                row=1,
            )
            async def play_5(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[2][0],
                style=discord.ButtonStyle.secondary,
                custom_id="6",
                disabled=self.board[2][0] != "-" or self.winner is not None or disable_on_timeout,
                row=2,
            )
            async def play_6(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[2][1],
                style=discord.ButtonStyle.secondary,
                custom_id="7",
                disabled=self.board[2][1] != "-" or self.winner is not None or disable_on_timeout,
                row=2,
            )
            async def play_7(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            @discord.ui.button(
                label=self.board[2][2],
                style=discord.ButtonStyle.secondary,
                custom_id="8",
                disabled=self.board[2][2] != "-" or self.winner is not None or disable_on_timeout,
                row=2,
            )
            async def play_8(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id not in [
                    self.player1.id,
                    self.player2.id if self.player2 != "tanjun" else "tanjun",
                ]:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourGame"),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                await self.make_move(interaction, int(button.custom_id))

            async def make_move(self, interaction: discord.Interaction, place: int):
                place = int(place)

                if place < 0 or place > 8:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.invalidMove"),
                        ephemeral=True,
                    )
                    return

                if self.board[place // 3][place % 3] != "-":
                    await interaction.followup.send(
                        tanjunLocalizer.localize(
                            interaction.locale,
                            "commands.games.ticTacToe.cellAlreadyTaken",
                        ),
                        ephemeral=True,
                    )
                    return

                if interaction.user != self.current_player:
                    await interaction.followup.send(
                        tanjunLocalizer.localize(str(interaction.locale), "commands.games.ticTacToe.notYourTurn"),
                        ephemeral=True,
                    )
                    return

                self.board[place // 3][place % 3] = (
                    self.player1_move if self.current_player == self.player1 else self.player2_move
                )
                self.toggle_turn()

                if self.check_winners():
                    await self.update_board(interaction)
                    return

                if self.player2 == "tanjun" or self.player2.bot:
                    self.current_player = self.player2
                    _, best_move = self.minimax(self.current_player, self.bot_difficulty * 2, self.board, True)
                    self.board[best_move // 3][best_move % 3] = self.player2_move
                    self.current_player = self.player1

                await self.update_board(interaction)

            def check_winners(self):
                if self.check_winner():
                    self.game_over = True
                    self.winner = self.check_winner()
                    return True

                if self.is_full():
                    self.game_over = True
                    return True
                return False

        return TicTacToeView(self)


async def tic_tac_toe(
    commandInfo: utility.commandInfo,
    player1: discord.Member,
    player2: discord.Member = None,
):
    if player2 is None:
        player2 = "tanjun"

    ticTacToe = TicTacToe(player1, player2)
    await ticTacToe.update_board(commandInfo, initial=True)
