import utility
import discord
from localizer import tanjunLocalizer
import random
from commands.games.hangman_words.words import words

hangmanSteps = [
    """







    """,
    """






_____
    """,
    """

 |
 |
 |
 |
 |
_|___
    """,
    """
  _______
 |
 |
 |
 |
 |
_|___
    """,
    """
  _______
 |/      
 |
 |
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |
 |
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |       |
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |      /|
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |      /|\\
 |
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |      /|\\
 |      /
 |
_|___
    """,
    """
  _______
 |/      |
 |      🥺
 |      /|\\
 |      / \\
 |
_|___
    """,
]


def get_guessed_letters(guesses: list[str], word: str):
    guessed_letters = ""
    if word in guesses:
        return word
    for letter in word:
        if letter in guesses:
            guessed_letters += letter
        elif letter == " ":
            guessed_letters += " "
        else:
            guessed_letters += "_"
    return guessed_letters

def wrong_letters(guesses: list[str], word):
    return len([x for x in guesses if len(x) == 1 and x != word and x not in word])

async def hangman(commandInfo: utility.commandInfo, language: str = "own"):
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
    allowed_words = words(language)

    word = random.choice(allowed_words)

    guesses = []

    async def update_hangman_game(
        interaction: discord.Interaction,
        given_up: bool = False,
        wrong_guess: bool = False,
    ):
        hanged_man = hangmanSteps[wrong_letters(guesses, word)]
        guessed_letters = get_guessed_letters(guesses, word)
        if given_up:
            hanged_man = hangmanSteps[wrong_letters(guesses, word) - 7]
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.givenUp.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.givenUp.description",
                    guesses=len(guesses) - 7,
                    guessed_letters=guessed_letters,
                    hanged_man=hanged_man,
                    used_letters=[x for x in guesses if len(x) == 1],
                ),
            )
        elif wrong_letters >= 11:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.failure.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.failure.description",
                    word=word,
                    hanged_man=hanged_man,
                    guessed_letters=guessed_letters,
                    used_letters=[x for x in guesses if len(x) == 1],
                ),
            )
        elif len(guesses) > 0 and guesses[-1] == word:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.success.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.success.description",
                    hanged_man=hanged_man,
                    guessed_letters=guessed_letters,
                    guesses=len(guesses),
                    used_letters=[x for x in guesses if len(x) == 1],
                ),
            )
        elif wrong_guess:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.wrongGuess.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.wrongGuess.description",
                    guesses=len(guesses),
                    hanged_man=hanged_man,
                    guessed_letters=guessed_letters,
                    used_letters=[x for x in guesses if len(x) == 1],
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.description",
                    guesses=len(guesses),
                    hanged_man=hanged_man,
                    guessed_letters=guessed_letters,
                    used_letters=", ".join(
                        [
                            f"{letter}"
                            for letter in [x for x in guesses if len(x) == 1]
                        ]
                    ),
                ),
            )
        view = (
            None
            if len(guesses) > 11
            or (len(guesses) > 0 and guesses[-1] == word)
            or given_up
            else WordleView(commandInfo)
        )
        await interaction.response.edit_message(embed=embed, view=view)

    class HangmanInputModal(discord.ui.Modal):
        def __init__(self, commandInfo: utility.commandInfo, config):
            super().__init__(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.games.hangman.modal.title"
                )
            )
            self.commandInfo = commandInfo

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(
                        commandInfo.locale, "commands.games.hangman.modal.input.label"
                    ),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.games.hangman.modal.input.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction):
            # Parse input and update configurations
            try:
                guess = self.children[0].value.lower()

                if len(guess) > 1:
                    if guess != word:
                        guesses.append("THISAINTBEINGTHEWORD")
                        await update_hangman_game(interaction, wrong_guess=True)
                        return

                guesses.append(guess)

                await update_hangman_game(interaction)
            except ValueError:
                raise
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(
                        self.commandInfo.locale, "commands.games.hangman.error.title"
                    ),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.games.hangman.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    class WordleView(discord.ui.View):
        def __init__(self, commandInfo: utility.commandInfo):
            super().__init__(timeout=3600)
            self.commandInfo = commandInfo

        @discord.ui.button(label="Guess", style=discord.ButtonStyle.green)
        async def guess_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if interaction.user.id != commandInfo.user.id:
                await interaction.response.send_message(tanjunLocalizer.localize(commandInfo.locale, "commands.games.hangman.notYourGame"), ephemeral=True)
                return
            modal = HangmanInputModal(self.commandInfo, guesses)
            await interaction.response.send_modal(modal)
            self.stop()

        @discord.ui.button(label="Give up", style=discord.ButtonStyle.red)
        async def give_up_button_callback(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if interaction.user.id != commandInfo.user.id:
                await interaction.response.send_message(tanjunLocalizer.localize(commandInfo.locale, "commands.games.hangman.notYourGame"), ephemeral=True)
                return
            guesses.append(word)
            guesses.append("THISAINTBEINGTHEWORD")
            guesses.append("THISAINTBEINGTHEWORD")
            guesses.append("THISAINTBEINGTHEWORD")
            guesses.append("THISAINTBEINGTHEWORD")
            guesses.append("THISAINTBEINGTHEWORD")
            guesses.append("THISAINTBEINGTHEWORD")
            await update_hangman_game(interaction, given_up=True)
            self.stop()

    view = WordleView(commandInfo)
    hanged_man = hangmanSteps[wrong_letters(guesses, word)]
    guessed_letters = get_guessed_letters(guesses, word)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.hangman.initial.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.games.hangman.initial.description",
            guesses=len(guesses),
            hanged_man=hanged_man,
            guessed_letters=guessed_letters,
            used_letters=", ".join(
                [f"{letter}" for letter in [x for x in guesses if len(x) == 1]]
            ),
        ),
    )
    await commandInfo.reply(view=view, embed=embed)
