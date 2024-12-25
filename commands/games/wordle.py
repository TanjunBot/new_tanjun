import commands.games.wordle_words.words as words
import discord
import random
from localizer import tanjunLocalizer
import utility
from PIL import Image, ImageDraw, ImageFont
import io


def generate_wordle_background():
    # Create a new image with a purple background
    width = 500
    height = 600
    img = Image.new("RGBA", (width, height), (20, 20, 20, 255))
    draw = ImageDraw.Draw(img)

    # Calculate spacing to evenly distribute rectangles
    rect_width = 80
    rect_height = 80

    # Calculate padding to center the grid
    h_padding = (
        width - (5 * rect_width)
    ) // 6  # Horizontal padding between rectangles and edges
    v_padding = (
        height - (6 * rect_height)
    ) // 7  # Vertical padding between rectangles and edges

    # Draw rectangles in a 5x6 grid
    for row in range(6):
        for col in range(5):
            x1 = h_padding + col * (rect_width + h_padding)
            y1 = v_padding + row * (rect_height + v_padding)
            x2 = x1 + rect_width
            y2 = y1 + rect_height

            draw.rectangle(xy=(x1, y1, x2, y2), fill=(59, 59, 59, 255))

    # Save image to file
    img.save("wordle_background.png")


async def wordle(commandInfo: utility.commandInfo, language: str = "own"):
    locale = str(commandInfo.locale)
    if language == "own":
        language = locale
    if language in ["en-US", "en-GB"]:
        language = "en"
    elif language in ["zh-CH", "zh-TW"]:
        language = "zh"
    elif language in ["es-419", "es-ES"]:
        language = "es"
    elif language in ["pt-BR", "pt-PT"]:
        language = "pt"
    allowed_words = words.allowed_words(language)
    possible_words = words.possible_words(language)

    word = random.choice(possible_words)

    guesses = []

    async def generate_wordle_image(guesses: list[str], word: str):
        image = Image.open("assets/wordle_background.png")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("assets/fonts/Arial.ttf", 70)

        if language == "ja":
            font = ImageFont.truetype("assets/fonts/NotoSansJP.ttf", 70)
        elif language == "ko":
            font = ImageFont.truetype("assets/fonts/NotoSansKR.ttf", 70)
        elif language == "zh":
            font = ImageFont.truetype("assets/fonts/NotoSansSC.ttf", 70)
        elif language == "hi":
            font = ImageFont.truetype("assets/fonts/NotoSansThai.ttf", 70)

        # Calculate spacing to evenly distribute rectangles (same as background generation)
        width = 500
        height = 600
        rect_width = 80
        rect_height = 80
        h_padding = (
            width - (5 * rect_width)
        ) // 6  # Horizontal padding between rectangles and edges
        v_padding = (
            height - (6 * rect_height)
        ) // 7  # Vertical padding between rectangles and edges

        for i, guess in enumerate(guesses):
            if guess == "NOTHING":
                continue
            for j, char in enumerate(guess):
                # Calculate box position (same as background generation)
                x1 = h_padding + j * (rect_width + h_padding)
                y1 = v_padding + i * (rect_height + v_padding)

                # Determine color based on letter match
                if char == word[j]:
                    color = (0, 255, 0)  # Green for correct position
                elif char in word:
                    color = (255, 255, 0)  # Yellow for wrong position
                else:
                    color = (255, 0, 0)  # Red for not in word

                # Draw the box
                draw.rectangle(
                    xy=(x1, y1, x1 + rect_width, y1 + rect_height), fill=color
                )

                # Get text size for centering
                text_bbox = draw.textbbox((0, 0), char.upper(), font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]

                # Calculate centered position with a slight upward adjustment
                text_x = x1 + (rect_width - text_width) // 2
                text_y = (
                    y1
                    + (rect_height - text_height) // 2
                    - 15
                    - (10 if language == "ja" else 0)
                )

                # Draw the letter centered in the box
                utility.draw_text_with_outline(
                    draw,
                    (text_x, text_y),
                    char.upper(),
                    font,
                    (255, 255, 255, 255),  # White text
                    (0, 0, 0, 255),  # Black outline
                )

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        return img_byte_arr

    async def update_wordle_game(
        interaction: discord.Interaction, given_up: bool = False
    ):
        img_byte_arr = await generate_wordle_image(guesses, word)
        if given_up:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.givenUp.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.givenUp.description",
                    guesses=len(guesses) - 7,
                ),
            )
        elif len(guesses) >= 6:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.failure.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.failure.description",
                    word=word,
                ),
            )
        elif len(guesses) > 0 and guesses[-1] == word:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.success.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.success.description",
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.wordle.description",
                    guesses=len(guesses),
                ),
            )
        embed.set_image(url="attachment://wordle.png")
        view = (
            None
            if len(guesses) > 6
            or (len(guesses) > 0 and guesses[-1] == word)
            or given_up
            else WordleView(commandInfo)
        )
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            embed=embed,
            attachments=[discord.File(img_byte_arr, filename="wordle.png")],
            view=view,
        )

    class WordleInputModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo, config):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.wordle.modal.title"
                )
            )
            self.commandInfo = commandInfo

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.wordle.modal.input.label"
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.games.wordle.modal.input.placeholder",
                    ),
                    max_length=5,
                    min_length=5,
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            # Parse input and update configurations
            try:
                guess = self.children[0].value.lower()

                if guess.lower() not in allowed_words:
                    embed = utility.tanjunEmbed(
                        title=tanjunLocalizer.localize(
                            self.commandInfo.locale, "commands.games.wordle.error.title"
                        ),
                        description=tanjunLocalizer.localize(
                            self.commandInfo.locale,
                            "commands.games.wordle.error.invalidInput",
                        ),
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                guesses.append(guess)

                await update_wordle_game(interaction)
            except ValueError:
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.games.wordle.error.title"
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.games.wordle.error.invalidInput",
                    ),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

    class WordleView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo):
            super().__init__(timeout=3600)
            self.commandInfo = commandInfo

        @discord.ui.button(label="Guess", style=discord.ButtonStyle.green)
        async def guess_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.wordle.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            modal = WordleInputModal(self.commandInfo, guesses)
            await interaction.response.send_modal(modal)
            self.stop()

        @discord.ui.button(label="Give up", style=discord.ButtonStyle.red)
        async def give_up_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            await interaction.response.defer()
            if interaction.user.id != commandInfo.user.id:
                await interaction.followup.send(
                    tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.wordle.notYourGame"
                    ),
                    ephemeral=True,
                )
                return
            guesses.append(word)
            guesses.append("NOTHING")
            guesses.append("NOTHING")
            guesses.append("NOTHING")
            guesses.append("NOTHING")
            guesses.append("NOTHING")
            guesses.append("NOTHING")
            await update_wordle_game(interaction, given_up=True)
            self.stop()

    view = WordleView(commandInfo)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.wordle.initial.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.wordle.initial.description",
            guesses=len(guesses),
        )
        + (
            f"\n\n{tanjunLocalizer.localize(commandInfo.locale, 'commands.games.wordle.initial.descriptionextra.ja')}"
            if language == "ja"
            else ""
        ),
    )
    embed.set_image(url="attachment://wordle.png")
    img_byte_arr = await generate_wordle_image(guesses, word)
    await commandInfo.reply(
        view=view, embed=embed, file=discord.File(img_byte_arr, filename="wordle.png")
    )
