from locale_keys import locale
import contextlib
import random
from typing import Any
import discord
import utility
SHIPS = [('Carrier', 5, '🟥'), ('Battleship', 4, '🟧'), ('Cruiser', 3, '🟨'), ('Submarine', 3, '🟩'), ('Destroyer', 2, '🟪')]
WATER = '🟦'
HIT = '💥'
MISS = '⬜'
SHIP_SUNK = '🔥'
BOARD_SIZE = 10
ROW_LABELS = 'ABCDEFGHIJ'
COL_LABELS = '0123456789'

class Battleship:
    """A Battleship game between two players with auto-placement."""

    def __init__(self, player1: discord.Member, player2: discord.Member | None=None) -> None:
        self.player1 = player1
        self.player2 = player2 or 'tanjun'
        self.is_bot_game = self.player2 == 'tanjun'
        self.board1: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.board2: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.view1: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.view2: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.ships1: list[dict[str, Any]] = []
        self.ships2: list[dict[str, Any]] = []
        self.current_player: discord.Member | str = player1
        self.winner: discord.Member | str | None = None
        self.game_over = False
        self._generate_random_placement(self.board1, self.ships1)
        self._generate_random_placement(self.board2, self.ships2)
        self.message = None

    @staticmethod
    def _generate_random_placement(board: list[list[str]], ships_list: list[dict[str, Any]]) -> None:
        """Randomly place ships on a board."""
        ships_list.clear()
        for name, size, symbol in SHIPS:
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                direction = random.choice(['H', 'V'])
                if direction == 'H':
                    row = random.randint(0, BOARD_SIZE - 1)
                    col = random.randint(0, BOARD_SIZE - size)
                else:
                    row = random.randint(0, BOARD_SIZE - size)
                    col = random.randint(0, BOARD_SIZE - 1)
                if Battleship._can_place(board, row, col, size, direction):
                    cells = []
                    for i in range(size):
                        if direction == 'H':
                            board[row][col + i] = symbol
                            cells.append((row, col + i))
                        else:
                            board[row + i][col] = symbol
                            cells.append((row + i, col))
                    ships_list.append({'name': name, 'symbol': symbol, 'cells': cells, 'hits': 0, 'sunk': False})
                    placed = True
                attempts += 1

    @staticmethod
    def _can_place(board: list[list[str]], row: int, col: int, size: int, direction: str) -> bool:
        """Check if a ship can be placed without overlapping."""
        for i in range(size):
            r, c = (row + i, col) if direction == 'V' else (row, col + i)
            if r < 0 or r >= BOARD_SIZE or c < 0 or (c >= BOARD_SIZE):
                return False
            if board[r][c] != WATER:
                return False
        return True

    def _receive_attack(self, board: list[list[str]], ships_list: list[dict[str, Any]], row: int, col: int) -> str:
        """Process an attack on a board. Returns 'hit', 'miss', or 'sunk:Name'."""
        cell = board[row][col]
        if cell == WATER:
            board[row][col] = MISS
            return 'miss'
        if cell in (HIT, MISS, SHIP_SUNK):
            return 'already'
        ship_symbol = cell
        board[row][col] = HIT
        for ship in ships_list:
            if ship['symbol'] == ship_symbol:
                ship['hits'] += 1
                if ship['hits'] == len(ship['cells']):
                    ship['sunk'] = True
                    for sr, sc in ship['cells']:
                        board[sr][sc] = SHIP_SUNK
                    return f"sunk:{ship['name']}"
                return 'hit'
        return 'hit'

    def _all_ships_sunk(self, ships_list: list[dict[str, Any]]) -> bool:
        return all((ship['sunk'] for ship in ships_list))

    def _board_to_str(self, board: list[list[str]]) -> str:
        """Convert board to a string using emojis."""
        rows = []
        for i, row in enumerate(board):
            row_str = f'{ROW_LABELS[i]} '
            for cell in row:
                row_str += cell
            rows.append(row_str)
        header = '  ' + COL_LABELS
        return header + '\n' + '\n'.join(rows)

    def _format_battle_embed(self, locale: str, viewer: discord.Member | str | None=None) -> discord.Embed:
        """Build the battle phase embed showing both boards, personalized for the viewer."""
        p1_name = self.player1.display_name
        p2_name = self.player2.display_name if self.player2 != 'tanjun' else 'Tanjun'
        p1_own = self._board_to_str(self.board1)
        p1_view = self._board_to_str(self.view1)
        p2_own = self._board_to_str(self.board2)
        p2_view = self._board_to_str(self.view2)
        if viewer == self.player1:
            desc = f'## **{p1_name}** (your board)\n```\n{p1_own}\n```\n## **{p2_name}** (your view)\n```\n{p1_view}\n```\n'
        elif viewer == self.player2:
            desc = f'## **{p2_name}** (your board)\n```\n{p2_own}\n```\n## **{p1_name}** (your view)\n```\n{p2_view}\n```\n'
        else:
            desc = f'## **{p1_name}** (opponent view)\n```\n{p2_view}\n```\n## **{p2_name}** (opponent view)\n```\n{p1_view}\n```\n'
        if self.game_over:
            if self.winner:
                winner_name = self.winner.display_name if hasattr(self.winner, 'display_name') else 'Tanjun'
                desc += f'**{locale.commands.games.battleship.winner(locale, player=winner_name)}**'
            else:
                desc += f'**{locale.commands.games.battleship.gameOver(locale)}**'
        else:
            current = self.current_player.mention if self.current_player != 'tanjun' else 'Tanjun'
            desc += locale.commands.games.battleship.currentTurn(locale, player=current)
        legend = locale.commands.games.battleship.legend(locale, water=WATER, hit=HIT, miss=MISS, sunk=SHIP_SUNK)
        desc += f'\n**{legend}**'
        title = locale.commands.games.battleship.battleTitle(locale)
        return utility.tanjunEmbed(title=title, description=desc)

    async def _bot_turn(self, interaction: discord.Interaction) -> None:
        """Bot takes its turn - picks a random untargeted cell."""
        valid_targets = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board1[row][col] not in (HIT, MISS, SHIP_SUNK):
                    valid_targets.append((row, col))
        if not valid_targets:
            return
        row, col = random.choice(valid_targets)
        result = self._receive_attack(self.board1, self.ships1, row, col)
        if result == 'miss':
            self.view2[row][col] = MISS
        elif 'hit' in result or result == 'hit':
            self.view2[row][col] = HIT
        elif result.startswith('sunk:'):
            ship_name = result.split(':', 1)[1]
            for ship in self.ships1:
                if ship['name'] == ship_name:
                    for sr, sc in ship['cells']:
                        self.view2[sr][sc] = SHIP_SUNK
        if self._all_ships_sunk(self.ships1):
            self.winner = self.player2
            self.game_over = True
        self.current_player = self.player1

    async def show_board(self, interaction: discord.Interaction | utility.CommandInfo, initial: bool=False) -> None:
        """Display the current game state."""
        locale = str(interaction.locale)
        viewer = None
        if hasattr(interaction, 'user'):
            viewer = interaction.user
        embed = self._format_battle_embed(locale, viewer=viewer)
        view = BattleshipView(self, self.game_over)
        if initial:
            if hasattr(interaction, 'reply'):
                self.message = await interaction.reply(embed=embed, view=view)
            else:
                self.message = await interaction.followup.send(embed=embed, view=view)
        elif hasattr(interaction, 'edit_message'):
            await interaction.edit_message(embed=embed, view=view)
        else:
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=view)

class AttackModal(discord.ui.Modal, title='Enter Attack Coordinates'):
    """Modal for entering attack coordinates."""
    coordinate = discord.ui.TextInput(label='Coordinate (e.g., A5, B3, J9)', placeholder='Enter coordinate like A5', min_length=2, max_length=3)

    def __init__(self, game: Battleship) -> None:
        super().__init__()
        self.game = game

    async def on_submit(self, interaction: discord.Interaction) -> None:
        coord_str = self.coordinate.value.upper().strip()
        locale = str(interaction.locale)
        if len(coord_str) < 2:
            await interaction.response.send_message(locale.commands.games.battleship.error.invalidCoordinate(locale), ephemeral=True)
            return
        row_char = coord_str[0]
        col_str = coord_str[1:]
        if row_char not in ROW_LABELS:
            await interaction.response.send_message(locale.commands.games.battleship.error.invalidRow(locale), ephemeral=True)
            return
        try:
            col = int(col_str)
            if col < 0 or col >= BOARD_SIZE:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(locale.commands.games.battleship.error.invalidColumn(locale), ephemeral=True)
            return
        row = ROW_LABELS.index(row_char)
        view = BattleshipView(self.game, self.game.game_over)
        await view._handle_attack(interaction, row, col)

class BattleshipView(discord.ui.View):
    """View with attack modal and utility buttons."""

    def __init__(self, game: Battleship, disabled: bool=False) -> None:
        super().__init__(timeout=300)
        self.game = game
        attack_btn = discord.ui.Button(label='🎯 Attack', style=discord.ButtonStyle.primary, disabled=disabled or game.game_over, row=0)
        attack_btn.callback = self._attack_callback
        self.add_item(attack_btn)
        give_up = discord.ui.Button(label='🏳️ Give Up', style=discord.ButtonStyle.danger, row=0)
        give_up.callback = self._give_up_callback
        self.add_item(give_up)
        help_btn = discord.ui.Button(label='❓ Help', style=discord.ButtonStyle.secondary, row=0)
        help_btn.callback = self._help_callback
        self.add_item(help_btn)

    async def _attack_callback(self, interaction: discord.Interaction) -> None:
        """Open modal for coordinate input."""
        if self.game.game_over:
            return
        if interaction.user != self.game.current_player:
            await interaction.response.send_message(locale.commands.games.battleship.notYourTurn(str(interaction.locale)), ephemeral=True)
            return
        modal = AttackModal(self.game)
        await interaction.response.send_modal(modal)

    async def _handle_attack(self, interaction: discord.Interaction, row: int, col: int) -> None:
        if not interaction.response.is_done():
            await interaction.response.defer()
        game = self.game
        if game.game_over:
            return
        if game.current_player == game.player1:
            target_board = game.board2
            target_ships = game.ships2
            attacker_view = game.view1
        else:
            target_board = game.board1
            target_ships = game.ships1
            attacker_view = game.view2
        if target_board[row][col] in (HIT, MISS, SHIP_SUNK):
            await interaction.followup.send(locale.commands.games.battleship.alreadyAttacked(str(interaction.locale)), ephemeral=True)
            return
        result = game._receive_attack(target_board, target_ships, row, col)
        if result == 'miss':
            attacker_view[row][col] = MISS
        elif 'hit' in result or result == 'hit':
            attacker_view[row][col] = HIT
        elif result.startswith('sunk:'):
            ship_name = result.split(':', 1)[1]
            for ship in target_ships:
                if ship['name'] == ship_name:
                    for sr, sc in ship['cells']:
                        attacker_view[sr][sc] = SHIP_SUNK
        if game._all_ships_sunk(target_ships):
            game.winner = game.current_player
            game.game_over = True
            await game.show_board(interaction)
            return
        if game.is_bot_game:
            game.current_player = game.player2
            await game._bot_turn(interaction)
        else:
            game.current_player = game.player2 if game.current_player == game.player1 else game.player1
        await game.show_board(interaction)

    async def _give_up_callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        game = self.game
        if game.game_over:
            return
        if interaction.user != game.current_player:
            await interaction.followup.send(locale.commands.games.battleship.notYourGame(str(interaction.locale)), ephemeral=True)
            return
        game.winner = game.player2 if game.current_player == game.player1 else game.player1
        game.game_over = True
        await game.show_board(interaction)

    async def _help_callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        locale = str(interaction.locale)
        p1_name = self.game.player1.display_name
        p2_name = self.game.player2.display_name if self.game.player2 != 'tanjun' else 'Tanjun'
        if interaction.user not in (self.game.player1, self.game.player2 if isinstance(self.game.player2, discord.Member) else None):
            await interaction.followup.send(locale.commands.games.battleship.notYourGame(locale), ephemeral=True)
            return
        current_turn = self.game.current_player.display_name if hasattr(self.game.current_player, 'display_name') else 'Tanjun'
        enemy_board_text = locale.commands.games.battleship.helpEnemyBoard(locale, hit=HIT, miss=MISS, sunk=SHIP_SUNK)
        legend_text = locale.commands.games.battleship.legend(locale, water=WATER, hit=HIT, miss=MISS, sunk=SHIP_SUNK)
        msg = f'**{locale.commands.games.battleship.helpTitle(locale)}**\n\n📋 **{locale.commands.games.battleship.helpBoards(locale)}**\n- {locale.commands.games.battleship.helpYourBoard(locale)}\n- {enemy_board_text}\n\n🎯 **{locale.commands.games.battleship.helpToAttack(locale)}** {locale.commands.games.battleship.helpAttackInstruction(locale)}\n\n🏳️ **{locale.commands.games.battleship.helpGiveUp(locale)}** {locale.commands.games.battleship.helpGiveUpInstruction(locale)}\n\n📖 **{legend_text}**\n\n**{locale.commands.games.battleship.helpPlayers(locale)}** {locale.commands.games.battleship.helpPlayersValue(locale, p1=p1_name, p2=p2_name)}\n**{locale.commands.games.battleship.helpCurrentTurn(locale)}** {current_turn}'
        await interaction.followup.send(msg, ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.game.message:
            with contextlib.suppress(Exception):
                await self.game.message.edit(view=self)

async def battleship(command_info: utility.CommandInfo, player1: discord.Member, player2: discord.Member | None=None) -> None:
    """Start a Battleship game."""
    if player2 is None:
        player2 = 'tanjun'
    game = Battleship(player1, player2)
    await game.show_board(command_info, initial=True)