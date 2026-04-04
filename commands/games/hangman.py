import random
from typing import Any

import discord  # type: ignore[import-not-found]

import utility
from commands.games.hangman_words.words import words
from localizer import tanjunLocalizer

# flake8: noqa: E501 # No trailing whitespace (formatting for the hangman steps)
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


def get_guessed_letters(guesses: list[str], word: str) -> None:
    guessed_letters = ""
    if word in guesses:
        return word  # type: ignore[return-value]
    for letter in word:
        if letter in guesses:
            guessed_letters += letter
        elif letter == " ":
            guessed_letters += " "
        else:
            guessed_letters += "_"
    return guessed_letters  # type: ignore[return-value]


def wrong_letters(guesses: list[str], word) -> None:  # type: ignore[no-untyped-def]
    return len([x for x in guesses if len(x) == 1 and x != word and x not in word])  # type: ignore[return-value]


async def hangman(commandInfo: utility.CommandInfo, language: str = "own") -> None:
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

    guesses = []  # type: ignore[var-annotated]

    async def update_hangman_game(  # type: ignore[no-any-unimported]
        interaction: discord.Interaction,
        given_up: bool = False,
        wrong_guess: bool = False,
    ) -> None:
        hanged_man = hangmanSteps[wrong_letters(guesses, word)]  # type: ignore[call-overload,func-returns-value]
        guessed_letters = get_guessed_letters(guesses, word)  # type: ignore[func-returns-value]
        if given_up:
            hanged_man = hangmanSteps[wrong_letters(guesses, word)]  # type: ignore[call-overload,func-returns-value]
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.givenUp.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.games.hangman.givenUp.description",
                    guesses=len(guesses),
                    guessed_letters=guessed_letters if len(guessed_letters) > 0 else "",  # type: ignore[arg-type]
                    hanged_man=hanged_man,
                    used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
                ),
            )
        elif wrong_letters(guesses, word) >= 11:  # type: ignore[func-returns-value,operator]
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
                    used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
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
                    guessed_letters=guessed_letters if len(guessed_letters) > 0 else "",  # type: ignore[arg-type]
                    guesses=len(guesses),
                    used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
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
                    used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
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
                    guessed_letters=guessed_letters if len(guessed_letters) > 0 else "",  # type: ignore[arg-type]
                    used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
                ),
            )
        view = (
            None
            if wrong_letters(guesses, word) > 11 or (len(guesses) > 0 and guesses[-1] == word) or given_up  # type: ignore[func-returns-value,operator]
            else WordleView(commandInfo)
        )
        await interaction.response.edit_message(embed=embed, view=view)

    class HangmanInputModal(discord.ui.Modal):  # type: ignore[misc,no-any-unimported]
        def __init__(self, commandInfo: utility.CommandInfo, config) -> None:  # type: ignore[no-untyped-def]
            super().__init__(title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.modal.title"))
            self.commandInfo = CommandInfo  # type: ignore[name-defined]

            self.add_item(
                discord.ui.TextInput(
                    label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.modal.input.label"),
                    placeholder=tanjunLocalizer.localize(
                        commandInfo.locale,
                        "commands.games.hangman.modal.input.placeholder",
                    ),
                    required=True,
                )
            )

        async def on_submit(self, interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
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
                embed = utility.tanjunEmbed(
                    title=tanjunLocalizer.localize(self.commandInfo.locale, "commands.games.hangman.error.title"),
                    description=tanjunLocalizer.localize(
                        self.commandInfo.locale,
                        "commands.games.hangman.error.invalidInput",
                    ),
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

    class WordleView(discord.ui.View):  # type: ignore[misc,no-any-unimported]
        def __init__(self, commandInfo: utility.CommandInfo) -> None:
            super().__init__(timeout=3600)
            self.commandInfo = CommandInfo  # type: ignore[name-defined]

        @discord.ui.button(  # type: ignore[untyped-decorator]
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.buttons.guess"),
            style=discord.ButtonStyle.green,
        )
        async def guess_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[name-defined]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.notYourGame"),
                    ephemeral=True,
                )
                return
            modal = HangmanInputModal(self.commandInfo, guesses)
            await interaction.response.send_modal(modal)

        @discord.ui.button(  # type: ignore[untyped-decorator]
            label=tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.buttons.giveUp"),
            style=discord.ButtonStyle.red,
        )
        async def give_up_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button[Any]) -> None:  # type: ignore[misc,no-any-unimported]
            if interaction.user.id != CommandInfo.user.id:  # type: ignore[name-defined]
                await interaction.response.send_message(
                    tanjunLocalizer.localize(str(commandInfo.locale), "commands.games.hangman.notYourGame"),
                    ephemeral=True,
                )
                return
            guesses.append(word)
            await update_hangman_game(interaction, given_up=True)

    view = WordleView(commandInfo)
    hanged_man = hangmanSteps[wrong_letters(guesses, word)]  # type: ignore[call-overload,func-returns-value]
    guessed_letters = get_guessed_letters(guesses, word)  # type: ignore[func-returns-value]
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
            used_letters=", ".join([f"{letter}" for letter in [x for x in guesses if len(x) == 1]]),
        ),
    )
    await commandInfo.reply(view=view, embed=embed)
