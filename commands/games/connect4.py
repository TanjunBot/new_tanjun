import discord
import utility
from localizer import tanjunLocalizer
import random

class Connect4:
    def __init__(self, player1: discord.Member, player2: discord.Member = None, locale: str = "en", rows: int = 6, columns: int = 7):
        self.player1 = player1
        self.player2 = player2
        if self.player2 is None:
            self.player2 = "tanjun"
        self.empty_cell = "⚫"
        self.rows = rows
        self.columns = columns
        self.board = [[self.empty_cell for _ in range(columns)] for _ in range(rows)]
        self.current_player = self.player1
        self.selected_column = None
        self.game_over = False
        self.winner = None
        self.player1_move = "🔴"
        self.player2_move = "🟡"
        self.highlighted_emoji = "⚪"
        self.highlighted_column = 0
        self.message = None
        self.locale = locale
        self.bot_difficulty = random.randint(1, 5)

    def check_winner(self, board: list[list[str]] = None):
        if not board:
            board = self.board
        
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                # Horizontal check
                if j < self.columns - 3 and cell == row[j + 1] == row[j + 2] == row[j + 3] != self.empty_cell:
                    return cell
                # Vertical check
                if i < self.rows - 3 and cell == board[i + 1][j] == board[i + 2][j] == board[i + 3][j] != self.empty_cell:
                    return cell
                # Diagonal check (top-left to bottom-right)
                if i < self.rows - 3 and j < self.columns - 3 and cell == board[i + 1][j + 1] == board[i + 2][j + 2] == board[i + 3][j + 3] != self.empty_cell:
                    return cell
                # Diagonal check (top-right to bottom-left)
                if i < self.rows - 3 and j > 2 and cell == board[i + 1][j - 1] == board[i + 2][j - 2] == board[i + 3][j - 3] != self.empty_cell:
                    return cell
        return None
    
    def is_full(self, board: list[list[str]] = None):
        if not board:
            board = self.board
        for row in board:
            for cell in row:
                if cell == self.empty_cell:
                    return False
        return True
    
    def get_available_moves(self, board: list[list[str]] = None):
        if not board:
            board = self.board

        available_moves = []
        available_columns = self.available_columns()
        for column in available_columns:
            # Find the lowest empty cell in this column
            for row in range(self.rows - 1, -1, -1):
                if board[row][column] == self.empty_cell:
                    board_index = column + (row * self.columns)  # Convert to board index
                    available_moves.append(board_index)
                    break
        return available_moves

    def minimax_make_move(self, board: list[list[str]], move: int, player: str):
        # Create a copy of the board
        new_board = [row[:] for row in board]
        
        # The player parameter is now the actual symbol (X or O), not the player object
        new_board[move // self.columns][move % self.columns] = player
        return new_board

    def minimax(self, current_player: str, depth: int, board: list[list[str]], maximizing_player: bool):
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
        available_moves = self.get_available_moves(board)
        for move in available_moves:
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


    async def getBoardString(self):
        board_string = ""
        for j, row in enumerate(self.board):
            for i, cell in enumerate(row):
                if i == self.highlighted_column and j == 0:
                    board_string += self.highlighted_emoji
                else:
                    board_string += cell
            board_string += "\n"
        return board_string
    
    def available_columns(self):
        return [i for i, cell in enumerate(self.board[0]) if cell == self.empty_cell]

    async def update_board(
        self,
        interaction: discord.Interaction,
        initial: bool = False,
        timeout: bool = False,
    ):
        self.winner = self.check_winner()
        title = tanjunLocalizer.localize(
            interaction.locale, "commands.games.connect4.title"
        )
        description = tanjunLocalizer.localize(
            interaction.locale,
            "commands.games.connect4.description",
            player1=self.player1.mention,
            player2=self.player2.mention if self.player2 != "tanjun" else "Tanjun",
        )
        if self.player2 == "tanjun":
            description += "\n" + tanjunLocalizer.localize(
                interaction.locale,
                "commands.games.connect4.descriptionBotEnemy",
                difficulty=self.bot_difficulty,
            )
        if self.winner is not None:
            winner = self.player1 if self.winner == self.player1_move else self.player2
            description += "\n" + tanjunLocalizer.localize(
                interaction.locale,
                "commands.games.connect4.winner",
                winner=winner.mention if winner != "tanjun" else "Tanjun",
            )
        elif self.is_full():
            description += "\n" + tanjunLocalizer.localize(
                interaction.locale, "commands.games.connect4.draw"
            )
        else:
            description += "\n" + tanjunLocalizer.localize(
                interaction.locale,
                "commands.games.connect4.currentTurn",
                player=(
                    self.current_player.mention
                    if self.current_player != "tanjun"
                    else "Tanjun"
                ),
            )
        board_string = await self.getBoardString()
        embed = utility.tanjunEmbed(
            title=title, description=description + "\n\n" + board_string
        )
        if initial:
            self.message = await interaction.reply(embed=embed)
        view = self.getBoardView(
            timeout=3600, disable_on_timeout=timeout, message=self.message
        )
        if initial:
            await self.message.edit(view=view, embed=embed)
        else:
            await interaction.response.edit_message(view=view, embed=embed)

    async def drop(self, interaction: discord.Interaction):
        drop_column = self.highlighted_column
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][drop_column] == self.empty_cell:
                self.board[row][drop_column] = self.player1_move if self.current_player == self.player1 else self.player2_move
                break
        winner = self.check_winner()
        if winner:
            self.game_over = True

        if self.is_full():
            self.game_over = True
            await self.update_board(interaction)
            return

        if self.player2 == "tanjun" or self.player2.bot:
            await self.bot_move()
        else:
            self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        if not self.highlighted_column in self.available_columns():
            self.highlighted_column = self.available_columns()[0]

        winner = self.check_winner()
        if winner:
            self.game_over = True
        if self.game_over:
            await self.update_board(interaction)
            return
        
        await self.update_board(interaction)

    async def bot_move(self):
        _, move = self.minimax(self.player2_move, int(self.bot_difficulty / 2) + 1, self.board, True)
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][move % self.columns] == self.empty_cell:
                self.board[row][move % self.columns] = self.player2_move
                break

    def getBoardView(self, timeout: int = 3600, disable_on_timeout: bool = False, message: discord.Message = None):
        class Connect4View(discord.ui.View):
            def __init__(self, connect4: Connect4):
                super().__init__(timeout=timeout)
                self.connect4 = connect4

            async def on_timeout(self):
                for child in self.children:
                    child.disabled = True

                await message.edit(view=self)

            @discord.ui.button(
                label="⬅️",
                style=discord.ButtonStyle.secondary,
                custom_id="left",
                disabled=len(self.available_columns()) == 0
                or self.winner is not None
                or disable_on_timeout,
                row=0,
            )
            async def move_left(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user.id != self.connect4.player1.id and (self.connect4.player2 == "tanjun" or interaction.user.id != self.connect4.player2.id):
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourGame"), ephemeral=True)
                    return
                
                if not interaction.user.id == self.connect4.current_player.id:
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourTurn"), ephemeral=True)
                    return
                
                highlighted_index = self.connect4.available_columns().index(self.connect4.highlighted_column)
                highlighted_index -= 1
                self.connect4.highlighted_column = self.connect4.available_columns()[highlighted_index]
                await self.connect4.update_board(interaction)

            @discord.ui.button(
                label=tanjunLocalizer.localize(self.locale, "commands.games.connect4.drop"),
                style=discord.ButtonStyle.secondary,
                custom_id="drop",
                disabled=len(self.available_columns()) == 0
                or self.winner is not None
                or disable_on_timeout,
                row=0,
            )
            async def drop(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user.id != self.connect4.player1.id and (self.connect4.player2 == "tanjun" or interaction.user.id != self.connect4.player2.id):
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourGame"), ephemeral=True)
                    return
                
                if not interaction.user.id == self.connect4.current_player.id:
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourTurn"), ephemeral=True)
                    return
                
                await self.connect4.drop(interaction)

            @discord.ui.button(
                label="➡️",
                style=discord.ButtonStyle.secondary,
                custom_id="right",
                disabled=len(self.available_columns()) == 0
                or self.winner is not None
                or disable_on_timeout,
                row=0,
            )
            async def move_right(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                if interaction.user.id != self.connect4.player1.id and (self.connect4.player2 == "tanjun" or interaction.user.id != self.connect4.player2.id):
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourGame"), ephemeral=True)
                    return
                
                if not interaction.user.id == self.connect4.current_player.id:
                    await interaction.response.send_message(tanjunLocalizer.localize(interaction.locale, "commands.games.connect4.notYourTurn"), ephemeral=True)
                    return

                highlighted_index = self.connect4.available_columns().index(self.connect4.highlighted_column)
                highlighted_index += 1
                if highlighted_index >= len(self.connect4.available_columns()):
                    highlighted_index = 0
                self.connect4.highlighted_column = self.connect4.available_columns()[highlighted_index]
                await self.connect4.update_board(interaction)

        return Connect4View(self)


async def connect4(
    commandInfo: utility.commandInfo,
    player1: discord.Member,
    player2: discord.Member = None,
    rows: int = 6,
    columns: int = 7,
):
    # Add some reasonable limits to prevent massive boards
    rows = min(max(4, rows), 12)  # Minimum 4, Maximum 12
    columns = min(max(4, columns), 12)  # Minimum 4, Maximum 12
    connect4 = Connect4(player1, player2, commandInfo.locale, rows, columns)
    await connect4.update_board(commandInfo, initial=True)
