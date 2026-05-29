import io
import random
from typing import Any

import discord
from PIL import Image, ImageDraw, ImageFont

import commands.games.wordle_words.words as words
import utility
from localizer import tanjunLocalizer
from services.wordle_service import (
    generate_share_text,
    upsert_wordle_stats,
    validate_hard_mode_guess,
)
from utility import CommandInfo

# Color palette inspired by official Wordle
GREEN = (106, 170, 100)
YELLOW = (201, 180, 88)
DARK_GRAY = (58, 58, 60)
LIGHT_GRAY = (129, 131, 132)
OUTLINE = (60, 60, 60)
BG_COLOR = (18, 18, 19)
TILE_SIZE = 62
TILE_GAP = 5
GRID_COLS = 5
GRID_ROWS = 6
PADDING = 30
FONT_SIZE = 36  # px


def _get_font_path(language: str) -> str:
    """Return the best font path for the given language."""
    font_map = {
        "ja": "assets/fonts/NotoSansJP.ttf",
        "ko": "assets/fonts/NotoSansKR.ttf",
        "zh": "assets/fonts/NotoSansSC.ttf",
        "hi": "assets/fonts/NotoSansThai.ttf",
    }
    return font_map.get(language, "assets/fonts/Arial.ttf")


def _draw_tile(
    draw: ImageDraw.Draw,
    x: int,
    y: int,
    char: str,
    color: tuple[int, int, int],
    font: ImageFont.FreeTypeFont,
) -> None:
    """Draw a single Wordle tile with letter and outline."""
    # Tile background
    draw.rounded_rectangle(
        xy=(x, y, x + TILE_SIZE, y + TILE_SIZE),
        radius=4,
        fill=color,
        outline=OUTLINE if color == DARK_GRAY else None,
        width=1,
    )
    # Centered letter
    bbox = draw.textbbox((0, 0), char.upper(), font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    lx = x + (TILE_SIZE - tw) // 2
    ly = y + (TILE_SIZE - th) // 2 - 4
    utility.draw_text_with_outline(
        draw,
        (lx, ly),
        char.upper(),
        font,
        (255, 255, 255, 255),
        (20, 20, 20, 200),
    )


def _evaluate_guess(guess: str, word: str) -> list[tuple[int, int, int]]:
    """Return color for each position: green, yellow, or dark gray."""
    colors: list[tuple[int, int, int]] = [DARK_GRAY] * 5
    remaining = list(word)

    # First pass: exact matches
    for i in range(5):
        if guess[i] == remaining[i]:
            colors[i] = GREEN
            remaining[i] = None  # type: ignore[assignment]

    # Second pass: wrong position
    for i in range(5):
        if colors[i] == GREEN:
            continue
        if guess[i] in remaining:
            colors[i] = YELLOW
            remaining[remaining.index(guess[i])] = None  # type: ignore[arg-type]

    return colors


async def generate_wordle_image(
    guesses: list[str],
    word: str,
    language: str = "en",
) -> io.BytesIO:
    """Generate a higher-quality Wordle grid image."""
    font = ImageFont.truetype(_get_font_path(language), FONT_SIZE)

    grid_w = GRID_COLS * TILE_SIZE + (GRID_COLS - 1) * TILE_GAP
    grid_h = GRID_ROWS * TILE_SIZE + (GRID_ROWS - 1) * TILE_GAP
    img_w = grid_w + PADDING * 2
    img_h = grid_h + PADDING * 2

    img = Image.new("RGBA", (img_w, img_h), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = PADDING + col * (TILE_SIZE + TILE_GAP)
            y = PADDING + row * (TILE_SIZE + TILE_GAP)

            if row < len(guesses) and guesses[row] != "NOTHING":
                guess = guesses[row]
                if len(guess) > col:
                    char = guess[col]
                    color = _evaluate_guess(guess, word)[col]
                    _draw_tile(draw, x, y, char, color, font)
                else:
                    _draw_tile(draw, x, y, " ", DARK_GRAY, font)
            else:
                # Empty tile
                draw.rounded_rectangle(
                    xy=(x, y, x + TILE_SIZE, y + TILE_SIZE),
                    radius=4,
                    fill=DARK_GRAY,
                    outline=OUTLINE,
                    width=1,
                )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


async def wordle(command_info: utility.CommandInfo, language: str = "own") -> None:
    locale = str(command_info.locale)
    if language == "own":
        language = locale
    if language in ("en-US", "en-GB"):
        language = "en"
    elif language in ("zh-CH", "zh-TW"):
        language = "zh"
    elif language in ("es-419", "es-ES"):
        language = "es"
    elif language in ("pt-BR", "pt-PT"):
        language = "pt"

    allowed_words = words.allowed_words(language)
    possible_words = words.possible_words(language)
    word = random.choice(possible_words)

    guesses: list[str] = []
    hard_mode = False

    async def update_embed(
        interaction: discord.Interaction,
        given_up: bool = False,
    ) -> None:
        img_byte_arr = await generate_wordle_image(guesses, word, language)
        is_won = len(guesses) > 0 and not given_up and guesses[-1] == word
        is_lost = len(guesses) >= 6 or given_up

        if given_up:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.givenUp.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.givenUp.description",
                    guesses=len([g for g in guesses if g != "NOTHING"]),
                ),
            )
        elif is_won:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.success.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.success.description",
                ),
            )
        elif is_lost:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.failure.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.failure.description",
                    word=word,
                ),
            )
        else:
            mode_hint = " 🔴 Hard" if hard_mode else ""
            embed = utility.tanjunEmbed(
                title=f"{tanjunLocalizer.localize(command_info.locale, 'commands.games.wordle.title')}{mode_hint}",
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.description",
                    guesses=len(guesses),
                ),
            )

        embed.set_image(url="attachment://wordle.png")

        # Determine view
        game_over = is_won or is_lost
        view: discord.ui.View | None
        if game_over:
            view = WordleEndView(command_info, guesses, word, is_won, hard_mode)
        else:
            view = WordleGameView(command_info, guesses, word, hard_mode)

        await interaction.response.edit_message(
            embed=embed,
            attachments=[discord.File(img_byte_arr, filename="wordle.png")],
            view=view,
        )

    class WordleInputModal(discord.ui.Modal):
        def __init__(self, cmd_info: utility.CommandInfo) -> None:
            super().__init__(
                title=tanjunLocalizer.localize(str(cmd_info.locale), "commands.games.wordle.modal.title"),
            )
            self.command_info = cmd_info
            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        str(cmd_info.locale),
                        "commands.games.wordle.modal.input.label",
                    ),
                    placeholder=tanjunLocalizer.localize(
                        cmd_info.locale,
                        "commands.games.wordle.modal.input.placeholder",
                    ),
                    max_length=5,
                    min_length=5,
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction) -> None:
            guess = self.children[0].value.lower()  # type: ignore[attr-defined]

            if guess not in allowed_words:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.games.wordle.error.title",
                    ),
                    description=tanjunLocalizer.localize(
                        self.command_info.locale,
                        "commands.games.wordle.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Hard mode validation
            if hard_mode:
                error_msg = validate_hard_mode_guess(guess, guesses, word)
                if error_msg:
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(
                            self.command_info.locale,
                            "commands.games.wordle.error.title",
                        ),
                        description=error_msg,
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

            guesses.append(guess)
            await update_embed(interaction)

            # Save stats when game ends
            is_won = guess == word
            is_lost = len(guesses) >= 6
            if is_won or is_lost:
                try:
                    await upsert_wordle_stats(
                        user_id=str(command_info.user.id),
                        guild_id=str(command_info.guild.id) if command_info.guild else "0",
                        won=is_won,
                        guesses=len([g for g in guesses if g != "NOTHING"]),
                        hard_mode=hard_mode,
                    )
                except Exception:
                    pass  # Non-critical; don't disrupt the user experience

    class WordleGameView(discord.ui.View):
        def __init__(
            self,
            cmd_info: utility.CommandInfo,
            guess_list: list[str],
            target: str,
            hard: bool,
        ) -> None:
            super().__init__(timeout=3600)
            self.command_info = cmd_info
            self._guesses = guess_list
            self._word = target
            self._hard_mode = hard

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.buttons.guess"),
            style=discord.ButtonStyle.green,
        )
        async def guess_button_callback(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.notYourGame"),
                    ephemeral=True,
                )
                return
            modal = WordleInputModal(self.command_info)
            await interaction.response.send_modal(modal)

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.buttons.giveUp"),
            style=discord.ButtonStyle.red,
        )
        async def give_up_button_callback(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.notYourGame"),
                    ephemeral=True,
                )
                return
            # Fill remaining slots to show full grid
            while len(guesses) < 6:
                guesses.append("NOTHING")
            # Reveal word as last guess
            guesses.append(word)
            await update_embed(interaction, given_up=True)

            # Save stats (lost)
            try:
                await upsert_wordle_stats(
                    user_id=str(command_info.user.id),
                    guild_id=str(command_info.guild.id) if command_info.guild else "0",
                    won=False,
                    guesses=len([g for g in guesses if g != "NOTHING"]),
                    hard_mode=hard_mode,
                )
            except Exception:
                pass

    class WordleEndView(discord.ui.View):
        def __init__(
            self,
            cmd_info: utility.CommandInfo,
            guess_list: list[str],
            target: str,
            won: bool,
            hard: bool,
        ) -> None:
            super().__init__(timeout=3600)
            self.command_info = cmd_info
            self._guesses = guess_list
            self._word = target
            self._won = won
            self._hard_mode = hard

        @discord.ui.button(
            label="📋 Share",
            style=discord.ButtonStyle.secondary,
            emoji="📋",
        )
        async def share_button_callback(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.notYourGame"),
                    ephemeral=True,
                )
                return
            share_text = generate_share_text(
                self._guesses, self._word, self._won, self._hard_mode,
            )
            await interaction.response.send_message(
                f"```{share_text}```",
                ephemeral=True,
            )

    # --- Initial game setup ---

    class WordleStartView(discord.ui.View):
        def __init__(self, cmd_info: utility.CommandInfo) -> None:
            super().__init__(timeout=3600)
            self.command_info = cmd_info

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.buttons.playNormal"),
            style=discord.ButtonStyle.green,
        )
        async def normal_button_callback(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            nonlocal hard_mode
            hard_mode = False
            await _start_game(interaction)

        @discord.ui.button(
            label=tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.buttons.playHard"),
            style=discord.ButtonStyle.red,
        )
        async def hard_button_callback(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button[Any],
        ) -> None:
            nonlocal hard_mode
            hard_mode = True
            await _start_game(interaction)

        async def _start_game(self, interaction: discord.Interaction) -> None:
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[misc]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(command_info.locale), "commands.games.wordle.notYourGame"),
                    ephemeral=True,
                )
                return
            img_byte_arr = await generate_wordle_image(guesses, word, language)
            mode_hint = " 🔴 Hard" if hard_mode else ""
            embed = utility.tanjunEmbed(
                title=f"{tanjunLocalizer.localize(command_info.locale, 'commands.games.wordle.initial.title')}{mode_hint}",
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.games.wordle.initial.description",
                    guesses=0,
                )
                + (
                    f"\n\n{tanjunLocalizer.localize(str(command_info.locale), 'commands.games.wordle.initial.descriptionextra.ja')}"
                    if language == "ja"
                    else ""
                ),
            )
            embed.set_image(url="attachment://wordle.png")
            game_view = WordleGameView(self.command_info, guesses, word, hard_mode)
            await interaction.response.edit_message(
                embed=embed,
                attachments=[discord.File(img_byte_arr, filename="wordle.png")],
                view=game_view,
            )

    start_view = WordleStartView(command_info)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.games.wordle.pickMode.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.games.wordle.pickMode.description",
        ),
    )
    img_byte_arr = await generate_wordle_image(guesses, word, language)
    await command_info.reply(
        view=start_view,
        embed=embed,
        file=discord.File(img_byte_arr, filename="wordle.png"),
    )
