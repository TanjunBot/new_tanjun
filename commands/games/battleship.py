import random
from typing import Any

import discord

import utility
from localizer import tanjunLocalizer

# Ship definitions: (name, size, symbol)
SHIPS = [
    ("Carrier", 5, "🟥"),
    ("Battleship", 4, "🟧"),
    ("Cruiser", 3, "🟨"),
    ("Submarine", 3, "🟩"),
    ("Destroyer", 2, "🟦"),
]

# Emojis for the board
WATER = "🟦"
HIT = "💥"
MISS = "⬜"
SHIP_SUNK = "🔥"

BOARD_SIZE = 10

ROW_LABELS = "ABCDEFGHIJ"
COL_LABELS = "0123456789"


class Battleship:
    """A Battleship game between two players with auto-placement."""

    def __init__(self, player1: discord.Member, player2: discord.Member | None = None) -> None:
        self.player1 = player1
        self.player2 = player2 or "tanjun"  # type: ignore[assignment]
        self.is_bot_game = self.player2 == "tanjun"  # type: ignore[comparison-overlap]

        # Own boards (full grid with ship positions)
        self.board1: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.board2: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        # Opponent views (only hits, misses, sunk - rest is water)
        self.view1: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.view2: list[list[str]] = [[WATER] * BOARD_SIZE for _ in range(BOARD_SIZE)]

        self.ships1: list[dict[str, Any]] = []
        self.ships2: list[dict[str, Any]] = []

        self.current_player: discord.Member | str = player1
        self.winner: discord.Member | str | None = None
        self.game_over = False

        # Auto-place ships for both players
        self._generate_random_placement(self.board1, self.ships1)
        self._generate_random_placement(self.board2, self.ships2)

        self.message = None

    @staticmethod
    def _generate_random_placement(
        board: list[list[str]], ships_list: list[dict[str, Any]]
    ) -> None:
        """Randomly place ships on a board."""
        ships_list.clear()
        for name, size, symbol in SHIPS:
            placed = False
            attempts = 0
            while not placed and attempts < 200:
                direction = random.choice(["H", "V"])
                if direction == "H":
                    row = random.randint(0, BOARD_SIZE - 1)
                    col = random.randint(0, BOARD_SIZE - size)
                else:
                    row = random.randint(0, BOARD_SIZE - size)
                    col = random.randint(0, BOARD_SIZE - 1)

                if Battleship._can_place(board, row, col, size, direction):
                    cells = []
                    for i in range(size):
                        if direction == "H":
                            board[row][col + i] = symbol
                            cells.append((row, col + i))
                        else:
                            board[row + i][col] = symbol
                            cells.append((row + i, col))
                    ships_list.append({
                        "name": name,
                        "symbol": symbol,
                        "cells": cells,
                        "hits": 0,
                        "sunk": False,
                    })
                    placed = True
                attempts += 1

    @staticmethod
    def _can_place(
        board: list[list[str]], row: int, col: int, size: int, direction: str,
    ) -> bool:
        """Check if a ship can be placed without overlapping."""
        for i in range(size):
            r, c = (row + i, col) if direction == "V" else (row, col + i)
            if r < 0 or r >= BOARD_SIZE or c < 0 or c >= BOARD_SIZE:
                return False
            if board[r][c] != WATER:
                return False
        return True

    def _receive_attack(
        self, board: list[list[str]], ships_list: list[dict[str, Any]],
        row: int, col: int,
    ) -> str:
        """Process an attack on a board. Returns 'hit', 'miss', or 'sunk:Name'."""
        cell = board[row][col]
        if cell == WATER:
            board[row][col] = MISS
            return "miss"
        if cell in (HIT, MISS, SHIP_SUNK):
            return "already"
        # It's a ship symbol - find which ship
        ship_symbol = cell
        board[row][col] = HIT
        for ship in ships_list:
            if ship["symbol"] == ship_symbol:
                ship["hits"] += 1
                if ship["hits"] == len(ship["cells"]):
                    ship["sunk"] = True
                    # Mark all cells of sunk ship
                    for sr, sc in ship["cells"]:
                        board[sr][sc] = SHIP_SUNK
                    return f"sunk:{ship['name']}"
                return "hit"
        return "hit"

    def _all_ships_sunk(self, ships_list: list[dict[str, Any]]) -> bool:
        return all(ship["sunk"] for ship in ships_list)

    def _board_to_str(self, board: list[list[str]], show_ships: bool = False) -> str:
        """Convert board to a string using emojis."""
        rows = []
        for i, row in enumerate(board):
            row_str = f"{ROW_LABELS[i]} "
            for cell in row:
                row_str += cell
            rows.append(row_str)
        header = "  " + COL_LABELS
        return header + "\n" + "\n".join(rows)

    def _format_battle_embed(self, locale: str) -> discord.Embed:
        """Build the battle phase embed showing both boards."""
        p1_name = self.player1.display_name
        p2_name = self.player2.display_name if self.player2 != "tanjun" else "Tanjun"  # type: ignore[union-attr]

        # Player 1: own board and view of opponent
        p1_own = self._board_to_str(self.board1)
        p1_view = self._board_to_str(self.view1)

        # Player 2: own board and view of opponent
        p2_own = self._board_to_str(self.board2)
        p2_view = self._board_to_str(self.view2)

        desc = (
            f"## **{p1_name}**\n"
            f"```\n{p1_own}\n```\n"
            f"## **{p2_name}** (your view)\n"
            f"```\n{p2_view}\n```\n"
        )

        if self.game_over:
            if self.winner:
                winner_name = self.winner.display_name if hasattr(self.winner, "display_name") else "Tanjun"
                desc += f"**{tanjunLocalizer.localize(locale, 'commands.games.battleship.winner', player=winner_name)}**"
            else:
                desc += "**Game Over**"
        else:
            current = self.current_player.mention if self.current_player != "tanjun" else "Tanjun"
            desc += tanjunLocalizer.localize(locale, "commands.games.battleship.currentTurn", player=current)

        legend = (
            f"\n**Legend:** {WATER}=Water | {HIT}=Hit | {MISS}=Miss | {SHIP_SUNK}=Sunk"
        )
        desc += legend

        title = tanjunLocalizer.localize(locale, "commands.games.battleship.battleTitle")
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

        if result == "miss":
            self.view2[row][col] = MISS
        elif "hit" in result or result == "hit":
            self.view2[row][col] = HIT
        elif result.startswith("sunk:"):
            ship_name = result.split(":", 1)[1]
            for ship in self.ships1:
                if ship["name"] == ship_name:
                    for sr, sc in ship["cells"]:
                        self.view2[sr][sc] = SHIP_SUNK

        # Check if player1 lost
        if self._all_ships_sunk(self.ships1):
            self.winner = self.player2  # type: ignore[assignment]
            self.game_over = True

        # Switch back to player1
        self.current_player = self.player1

    async def show_board(
        self, interaction: discord.Interaction, initial: bool = False,
    ) -> None:
        """Display the current game state."""
        locale = str(interaction.locale)
        embed = self._format_battle_embed(locale)
        view = BattleshipView(self, self.game_over)

        if initial:
            self.message = await interaction.followup.send(embed=embed, view=view)  # type: ignore[attr-defined]
        else:
            await interaction.followup.edit_message(
                message_id=interaction.message.id, embed=embed, view=view,
            )


class BattleshipView(discord.ui.View):
    """View with the 10x10 attack grid for the current player."""

    def __init__(self, game: Battleship, disabled: bool = False) -> None:
        super().__init__(timeout=300)
        self.game = game

        # Add give-up button on row 0
        give_up = discord.ui.Button(label="🏳️ Give Up", style=discord.ButtonStyle.danger, row=0)
        give_up.callback = self._give_up_callback
        self.add_item(give_up)

        # Add help button
        help_btn = discord.ui.Button(label="❓ Help", style=discord.ButtonStyle.secondary, row=0)
        help_btn.callback = self._help_callback
        self.add_item(help_btn)

        # Create 10x10 grid of buttons (rows 1-10)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                button = discord.ui.Button(
                    label=f"{ROW_LABELS[row]}{col}",
                    style=discord.ButtonStyle.secondary,
                    custom_id=f"attack_{row}_{col}",
                    row=row + 1,
                    disabled=disabled or game.game_over,
                )
                button.callback = self._make_callback(row, col)
                self.add_item(button)

    def _make_callback(self, row: int, col: int):
        async def callback(interaction: discord.Interaction) -> None:
            await self._handle_attack(interaction, row, col)
        return callback

    async def _handle_attack(self, interaction: discord.Interaction, row: int, col: int) -> None:
        await interaction.response.defer()
        game = self.game

        if game.game_over:
            return

        # Check if it's the right player's turn
        if interaction.user != game.current_player:
            await interaction.followup.send(
                tanjunLocalizer.localize(
                    str(interaction.locale), "commands.games.battleship.notYourTurn",
                ),
                ephemeral=True,
            )
            return

        # Determine which board to attack
        if game.current_player == game.player1:
            target_board = game.board2
            target_ships = game.ships2
            attacker_view = game.view1
        else:
            target_board = game.board1
            target_ships = game.ships1
            attacker_view = game.view2

        # Check if already attacked
        if target_board[row][col] in (HIT, MISS, SHIP_SUNK):
            await interaction.followup.send(
                tanjunLocalizer.localize(
                    str(interaction.locale), "commands.games.battleship.alreadyAttacked",
                ),
                ephemeral=True,
            )
            return

        result = game._receive_attack(target_board, target_ships, row, col)

        # Update the attacker's view
        if result == "miss":
            attacker_view[row][col] = MISS
        elif "hit" in result or result == "hit":
            attacker_view[row][col] = HIT
        elif result.startswith("sunk:"):
            ship_name = result.split(":", 1)[1]
            for ship in target_ships:
                if ship["name"] == ship_name:
                    for sr, sc in ship["cells"]:
                        attacker_view[sr][sc] = SHIP_SUNK

        # Check if the game is over
        if game._all_ships_sunk(target_ships):
            game.winner = game.current_player
            game.game_over = True
            await game.show_board(interaction)
            return

        # Switch turns
        if game.is_bot_game:
            # Bot attacks back
            game.current_player = game.player2  # type: ignore[assignment]
            await game._bot_turn(interaction)
        else:
            game.current_player = game.player2 if game.current_player == game.player1 else game.player1  # type: ignore[assignment]

        await game.show_board(interaction)

    async def _give_up_callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        game = self.game
        if game.game_over:
            return
        if interaction.user != game.current_player:
            await interaction.followup.send(
                tanjunLocalizer.localize(
                    str(interaction.locale), "commands.games.battleship.notYourGame",
                ),
                ephemeral=True,
            )
            return

        # Determine winner: the other player
        game.winner = game.player2 if game.current_player == game.player1 else game.player1
        game.game_over = True
        await game.show_board(interaction)

    async def _help_callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        locale = str(interaction.locale)
        p1_name = self.game.player1.display_name
        p2_name = self.game.player2.display_name if self.game.player2 != "tanjun" else "Tanjun"  # type: ignore[union-attr]

        if interaction.user not in (self.game.player1, self.game.player2 if isinstance(self.game.player2, discord.Member) else None):
            await interaction.followup.send(
                tanjunLocalizer.localize(locale, "commands.games.battleship.notYourGame"),
                ephemeral=True,
            )
            return

        msg = (
            f"**Battleship Help**\n\n"
            f"📋 **Boards shown:**\n"
            f"- Your board (top) shows YOUR ships: colored blocks\n"
            f"- Enemy board (bottom) shows your attacks: {HIT} = hit, {MISS} = miss, {SHIP_SUNK} = sunk\n\n"
            f"🎯 **To attack:** Click a button on the grid below the boards.\n\n"
            f"🏳️ **Give up:** Click the Give Up button to concede.\n\n"
            f"📖 **Legend:** {WATER} Water | {HIT} Hit | {MISS} Miss | {SHIP_SUNK} Sunk\n\n"
            f"**Players:** {p1_name} vs {p2_name}\n"
            f"**Current turn:** {self.game.current_player.display_name if hasattr(self.game.current_player, 'display_name') else 'Tanjun'}"
        )
        await interaction.followup.send(msg, ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True  # type: ignore[attr-defined]
        if self.game.message:
            try:
                await self.game.message.edit(view=self)
            except Exception:
                pass


async def battleship(
    command_info: utility.CommandInfo,
    player1: discord.Member,
    player2: discord.Member | None = None,
) -> None:
    """Start a Battleship game."""
    if player2 is None:
        player2 = "tanjun"  # type: ignore[assignment]

    game = Battleship(player1, player2)
    await game.show_board(command_info, initial=True)
