from locale_keys import locale
import random
import discord
import utility
from commands.games.hangman_words.words import words
hangmanSteps = ['\n\n\n\n\n\n\n\n    ', '\n\n\n\n\n\n\n_____\n    ', '\n\n |\n |\n |\n |\n |\n_|___\n    ', '\n  _______\n |\n |\n |\n |\n |\n_|___\n    ', '\n  _______\n |/\n |\n |\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |\n |\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |       |\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |      /|\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |      /|\\\n |\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |      /|\\\n |      /\n |\n_|___\n    ', '\n  _______\n |/      |\n |      🥺\n |      /|\\\n |      / \\\n |\n_|___\n    ']

def get_guessed_letters(guesses: list[str], word: str):
    guessed_letters = ''
    if word in guesses:
        return word
    for letter in word:
        if letter in guesses:
            guessed_letters += letter
        elif letter == ' ':
            guessed_letters += ' '
        else:
            guessed_letters += '_'
    return guessed_letters

def wrong_letters(guesses: list[str], word):
    return len([x for x in guesses if len(x) == 1 and x != word and (x not in word)])

async def hangman(command_info: utility.command_info, language: str='own'):
    locale = str(command_info.locale)
    if language == 'own':
        language = locale
    if language in ['en-US', 'en-GB']:
        language = 'en'
    elif language in ['zh-CH', 'zh-TW']:
        language = 'zh'
    elif language in ['es-419', 'es-ES']:
        language = 'es'
    elif language in ['pt-BR', 'pt-PT']:
        language = 'pt'
    allowed_words = words(language)
    word = random.choice(allowed_words)
    guesses = []

    async def update_hangman_game(interaction: discord.Interaction, given_up: bool=False, wrong_guess: bool=False):
        hanged_man = hangmanSteps[wrong_letters(guesses, word)]
        guessed_letters = get_guessed_letters(guesses, word)
        if given_up:
            hanged_man = hangmanSteps[wrong_letters(guesses, word)]
            embed = utility.tanjunEmbed(title=locale.commands.games.hangman.givenUp.title(command_info.locale), description=locale.commands.games.hangman.givenUp.description(command_info.locale, guesses=len(guesses), guessed_letters=guessed_letters if len(guessed_letters) > 0 else '', hanged_man=hanged_man, used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
        elif wrong_letters(guesses, word) >= 11:
            embed = utility.tanjunEmbed(title=locale.commands.games.hangman.failure.title(command_info.locale), description=locale.commands.games.hangman.failure.description(command_info.locale, word=word, hanged_man=hanged_man, guessed_letters=guessed_letters, used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
        elif len(guesses) > 0 and guesses[-1] == word:
            embed = utility.tanjunEmbed(title=locale.commands.games.hangman.success.title(command_info.locale), description=locale.commands.games.hangman.success.description(command_info.locale, hanged_man=hanged_man, guessed_letters=guessed_letters if len(guessed_letters) > 0 else '', guesses=len(guesses), used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
        elif wrong_guess:
            embed = utility.tanjunEmbed(title=locale.commands.games.hangman.wrongGuess.title(command_info.locale), description=locale.commands.games.hangman.wrongGuess.description(command_info.locale, guesses=len(guesses), hanged_man=hanged_man, guessed_letters=guessed_letters, used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
        else:
            embed = utility.tanjunEmbed(title=locale.commands.games.hangman.title(command_info.locale), description=locale.commands.games.hangman.description(command_info.locale, guesses=len(guesses), hanged_man=hanged_man, guessed_letters=guessed_letters if len(guessed_letters) > 0 else '', used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
        view = None if wrong_letters(guesses, word) > 11 or (len(guesses) > 0 and guesses[-1] == word) or given_up else WordleView(command_info)
        await interaction.response.edit_message(embed=embed, view=view)

    class HangmanInputModal(discord.ui.Modal):

        def __init__(self, command_info: utility.command_info, config):
            super().__init__(title=locale.commands.games.hangman.modal.title(command_info.locale))
            self.command_info = command_info
            self.add_item(discord.ui.TextInput(label=locale.commands.games.hangman.modal.input.label(command_info.locale), placeholder=locale.commands.games.hangman.modal.input.placeholder(command_info.locale), required=True))

        async def on_submit(self, interaction: discord.Interaction):
            try:
                guess = self.children[0].value.lower()
                if len(guess) > 1 and guess != word:
                    guesses.append('THISAINTBEINGTHEWORD')
                    await update_hangman_game(interaction, wrong_guess=True)
                    return
                guesses.append(guess)
                await update_hangman_game(interaction)
            except ValueError:
                embed = utility.tanjunEmbed(title=locale.commands.games.hangman.error.title(self.command_info.locale), description=locale.commands.games.hangman.error.invalidInput(self.command_info.locale))
                await interaction.response.send_message(embed=embed, ephemeral=True)

    class WordleView(discord.ui.View):

        def __init__(self, command_info: utility.command_info):
            super().__init__(timeout=3600)
            self.command_info = command_info

        @discord.ui.button(label=locale.commands.games.hangman.buttons.guess(command_info.locale), style=discord.ButtonStyle.green)
        async def guess_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.games.hangman.notYourGame(command_info.locale), ephemeral=True)
                return
            modal = HangmanInputModal(self.command_info, guesses)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label=locale.commands.games.hangman.buttons.giveUp(command_info.locale), style=discord.ButtonStyle.red)
        async def give_up_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.games.hangman.notYourGame(command_info.locale), ephemeral=True)
                return
            guesses.append(word)
            await update_hangman_game(interaction, given_up=True)
    view = WordleView(command_info)
    hanged_man = hangmanSteps[wrong_letters(guesses, word)]
    guessed_letters = get_guessed_letters(guesses, word)
    embed = utility.tanjunEmbed(title=locale.commands.games.hangman.initial.title(command_info.locale), description=locale.commands.games.hangman.initial.description(command_info.locale, guesses=len(guesses), hanged_man=hanged_man, guessed_letters=guessed_letters, used_letters=', '.join([f'{letter}' for letter in [x for x in guesses if len(x) == 1]])))
    await command_info.reply(view=view, embed=embed)