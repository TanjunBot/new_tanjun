from locale_keys import locale
import random

_memory = locale.commands.games.memory

def _memory_text(loc: str, rel: str, **kwargs) -> str:
    node = _memory
    for part in rel.split('.'):
        node = getattr(node, part)
    return node(loc, **kwargs)
from typing import Any, cast
import discord
import utility
EMOJI_PAIRS = ['🍎', '🍊', '🍋', '🍇', '🍓', '🍒', '🍑', '🥝', '🍌', '🍉', '🍍', '🥭', '🍈', '🫐', '🍐', '🥥', '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🐧', '🐦', '🐤', '🦆', '🦅', '🦉', '🦇', '🐺', '🌻', '🌹', '🌸', '🌺', '🌷', '🌵', '🌲', '🍀', '⭐', '🌙', '☀️', '🌈', '⚡', '🔥', '💧', '❄️', '❤️', '💛', '💚', '💙', '💜', '🖤', '🤍', '🧡']
HIDDEN_EMOJI = '❓'
NUMBER_EMOJIS = {0: '0️⃣', 1: '1️⃣', 2: '2️⃣', 3: '3️⃣', 4: '4️⃣', 5: '5️⃣', 6: '6️⃣', 7: '7️⃣', 8: '8️⃣', 9: '9️⃣', 10: '🔟', 11: '1️⃣1️⃣', 12: '1️⃣2️⃣', 13: '1️⃣3️⃣', 14: '1️⃣4️⃣', 15: '1️⃣5️⃣', 16: '1️⃣6️⃣', 17: '1️⃣7️⃣', 18: '1️⃣8️⃣', 19: '1️⃣9️⃣', 20: '2️⃣0️⃣', 21: '2️⃣1️⃣', 22: '2️⃣2️⃣', 23: '2️⃣3️⃣', 24: '2️⃣4️⃣'}

class MemoryGame:
    """A classic Memory/Concentration card matching game."""

    def __init__(self, player: discord.Member, grid_size: int=4) -> None:
        self.player = player
        self.grid_size = grid_size
        self.total_cards = grid_size * grid_size
        self.num_pairs = self.total_cards // 2
        selected_emojis = random.sample(EMOJI_PAIRS, self.num_pairs)
        self.cards = selected_emojis + selected_emojis
        random.shuffle(self.cards)
        self.revealed: list[bool] = [False] * self.total_cards
        self.matched: list[bool] = [False] * self.total_cards
        self.first_selection: int | None = None
        self.turns = 0
        self.pairs_found = 0
        self.game_over = False
        self.message: discord.WebhookMessage | None = None

    def get_board_display(self) -> str:
        """Render the current board state as a string."""
        rows: list[str] = []
        for row in range(self.grid_size):
            row_cards: list[str] = []
            for col in range(self.grid_size):
                idx = row * self.grid_size + col
                if self.matched[idx]:
                    row_cards.append(self.cards[idx])
                elif self.revealed[idx]:
                    row_cards.append(self.cards[idx])
                else:
                    row_cards.append(HIDDEN_EMOJI)
            rows.append(' '.join(row_cards))
        return '\n'.join(rows)

    def get_button_labels(self) -> list[int]:
        """Return indices of cards that still have interactive buttons."""
        available: list[int] = []
        for i in range(self.total_cards):
            if not self.matched[i] and (not self.revealed[i]):
                available.append(i)
        return available

    def select_card(self, index: int) -> str | None:
        """
        Select a card. Returns None if game continues, or a result string
        if the turn completes (match or not).
        """
        if self.matched[index] or self.revealed[index] or self.game_over:
            return None
        self.revealed[index] = True
        if self.first_selection is None:
            self.first_selection = index
            return None
        second = index
        first = self.first_selection
        self.turns += 1
        if self.cards[first] == self.cards[second]:
            self.matched[first] = True
            self.matched[second] = True
            self.pairs_found += 1
            self.first_selection = None
            if self.pairs_found == self.num_pairs:
                self.game_over = True
                return 'win'
            return 'match'
        return 'no_match'

    def flip_back(self) -> None:
        """Flip back revealed cards that were not a match."""
        if self.first_selection is not None:
            idx = self.first_selection
            self.revealed[idx] = False
            self.first_selection = None

    def reset_revealed(self) -> None:
        """Reset all non-matched revealed cards."""
        for i in range(self.total_cards):
            if not self.matched[i]:
                self.revealed[i] = False
        self.first_selection = None

async def memory(command_info: utility.CommandInfo, player: discord.Member) -> None:
    """Start a Memory game against the bot."""
    locale = command_info.locale
    game = MemoryGame(player=player, grid_size=4)

    def localize(key: str, **kwargs: Any) -> str:
        rel = key.removeprefix('commands.games.memory.')
        return _memory_text(locale, rel, **kwargs)
    embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"{localize('commands.games.memory.rules_intro')}\n\n```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}", color=10181046)
    view = MemoryView(game, command_info)
    message = await command_info.reply(embed=embed, view=view)
    game.message = cast(discord.WebhookMessage, message)

class MemoryView(discord.ui.View):
    """Interactive view for the Memory card game."""

    def __init__(self, game: MemoryGame, command_info: utility.CommandInfo) -> None:
        super().__init__(timeout=300)
        self.game = game
        self.command_info = command_info
        self._build_buttons()

    def _build_buttons(self) -> None:
        """Create buttons for the current game state."""
        self.clear_items()
        for idx in range(self.game.total_cards):
            if self.game.matched[idx]:
                button = discord.ui.Button(label=self.game.cards[idx], style=discord.ButtonStyle.success, disabled=True, row=idx // self.game.grid_size)
            elif self.game.revealed[idx]:
                label = self.game.cards[idx]
                if self.game.first_selection is not None and idx == self.game.first_selection:
                    button = discord.ui.Button(label=label, style=discord.ButtonStyle.primary, disabled=True, row=idx // self.game.grid_size)
                else:
                    button = discord.ui.Button(label=label, style=discord.ButtonStyle.secondary, disabled=True, row=idx // self.game.grid_size)
            else:
                button = discord.ui.Button(label=NUMBER_EMOJIS.get(idx, str(idx)), style=discord.ButtonStyle.secondary, disabled=False, row=idx // self.game.grid_size)
                button.callback = self._make_callback(idx)
            self.add_item(button)

    def _make_callback(self, index: int):
        """Create a callback for a card selection button."""

        async def callback(interaction: discord.Interaction) -> None:
            if interaction.user != self.game.player:
                locale = self.command_info.locale
                not_your_game_msg = locale.commands.games.memory.not_your_game(locale)
                await interaction.response.send_message(not_your_game_msg, ephemeral=True)
                return
            await self._handle_selection(interaction, index)
        return callback

    async def _handle_selection(self, interaction: discord.Interaction, index: int) -> None:
        """Handle a card selection."""
        game = self.game
        locale = self.command_info.locale

        def localize(key: str, **kwargs: Any) -> str:
            rel = key.removeprefix('commands.games.memory.')
            return _memory_text(locale, rel, **kwargs)
        result = game.select_card(index)
        if result is None:
            self._build_buttons()
            embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}\n**{localize('commands.games.memory.select_second')}**", color=10181046)
            await interaction.response.edit_message(embed=embed, view=self)
        elif result == 'match':
            self._build_buttons()
            embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}\n✨ **{localize('commands.games.memory.match')}** ✨", color=3066993)
            if game.game_over:
                await self._end_game(interaction, embed, localize)
                return
            await interaction.response.edit_message(embed=embed, view=self)
        elif result == 'no_match':
            self._build_buttons()
            embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}\n❌ **{localize('commands.games.memory.no_match')}** ❌", color=15158332)
            await interaction.response.edit_message(embed=embed, view=self)
            game.reset_revealed()
            self._build_buttons()
            import asyncio
            await asyncio.sleep(1.5)
            embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}\n**{localize('commands.games.memory.select_first')}**", color=10181046)
            await interaction.edit_original_response(embed=embed, view=self)
        elif result == 'win':
            embed = utility.TanjunEmbed(title=localize('commands.games.memory.title'), description=f"```\n{game.get_board_display()}\n```\n\n**{localize('commands.games.memory.turns')}:** {game.turns} | **{localize('commands.games.memory.pairs_found')}:** {game.pairs_found}/{game.num_pairs}\n**{localize('commands.games.memory.player')}:** {game.player.display_name}\n🎉 **{localize('commands.games.memory.win')}** 🎉", color=15844367)
            await self._end_game(interaction, embed, localize)

    async def _end_game(self, interaction: discord.Interaction, embed: discord.Embed, localize: Any) -> None:
        """End the game and show the final state."""
        self.clear_items()
        button = discord.ui.Button(label=localize('commands.games.memory.game_over'), style=discord.ButtonStyle.success, disabled=True)
        self.add_item(button)
        await interaction.response.edit_message(embed=embed, view=self)