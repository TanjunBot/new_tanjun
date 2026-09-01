from locale_keys.nav import field_name
from locale_keys import locale
import difflib
import random
import discord
import utility
from commands.games.country_flags.flags import random_flag


def get_similarity(guess: str, answer: str) -> float:
    a, b = guess.lower(), answer.lower()
    r1 = difflib.SequenceMatcher(None, a, b).ratio()
    r2 = difflib.SequenceMatcher(None, b, a).ratio()
    return max(r1, r2) * 100


def get_hint(word: str) -> str:
    chars = list(word.lower())
    blanks = ['_'] * len(chars)
    num_reveals = max(1, len(chars) // 3)
    reveal_positions = random.sample(range(len(chars)), num_reveals)
    for pos in reveal_positions:
        blanks[pos] = chars[pos]
    return ''.join(blanks)


async def flag_quiz(command_info: utility.command_info):
    locale_str = str(command_info.locale)
    flag_file = random_flag()
    country_field = field_name(flag_file.replace('.png', ''))
    correct_country = getattr(locale.countries, country_field)(locale_str)
    guesses = []
    hints_used = 0

    async def update_game(interaction: discord.Interaction, given_up: bool=False, wrong_guess: bool=False, hint_used: bool=False):
        file = discord.File(f'commands/games/country_flags/{flag_file}', filename='flag.png')
        if given_up:
            embed = utility.tanjunEmbed(title=locale.commands.games.flagquiz.givenUp.title(command_info.locale), description=locale.commands.games.flagquiz.givenUp.description(command_info.locale, country=correct_country))
            embed.set_image(url='attachment://flag.png')
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, attachments=[file], view=None)
            return
        if len(guesses) > 0 and guesses[-1].lower() == correct_country.lower():
            embed = utility.tanjunEmbed(title=locale.commands.games.flagquiz.success.title(command_info.locale), description=locale.commands.games.flagquiz.success.description(command_info.locale, guesses=len(guesses)))
            embed.set_image(url='attachment://flag.png')
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, attachments=[file], view=None)
            return
        if len(guesses) >= 5:
            embed = utility.tanjunEmbed(title=locale.commands.games.flagquiz.failure.title(command_info.locale), description=locale.commands.games.flagquiz.failure.description(command_info.locale, country=correct_country))
            embed.set_image(url='attachment://flag.png')
            await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, attachments=[file], view=None)
            return
        guess_list = ''
        for guess in guesses:
            similarity = get_similarity(guess, correct_country)
            guess_list += f'\n{guess} - {similarity:.1f}% similar'
        if hint_used:
            hint = get_hint(correct_country)
            guess_list += f'\n\n{locale.commands.games.flagquiz.hint(command_info.locale)}: `{hint}`'
        embed = utility.tanjunEmbed(title=locale.commands.games.flagquiz.title(command_info.locale), description=locale.commands.games.flagquiz.description(command_info.locale, remaining=5 - len(guesses), guesses=guess_list))
        embed.set_image(url='attachment://flag.png')
        view = FlagQuizView(command_info)
        await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, attachments=[file], view=view)

    class FlagQuizModal(discord.ui.Modal):

        def __init__(self, command_info: utility.command_info):
            super().__init__(title=locale.commands.games.flagquiz.modal.title(command_info.locale))
            self.command_info = command_info
            self.add_item(discord.ui.TextInput(label=locale.commands.games.flagquiz.modal.input.label(command_info.locale), placeholder=locale.commands.games.flagquiz.modal.input.placeholder(command_info.locale), required=True))

        async def on_submit(self, interaction: discord.Interaction):
            guess = self.children[0].value.strip()
            guesses.append(guess)
            await update_game(interaction)

    class FlagQuizView(discord.ui.View):

        def __init__(self, command_info: utility.command_info):
            super().__init__(timeout=3600)
            self.command_info = command_info

        @discord.ui.button(label=locale.commands.games.flagquiz.buttons.guess(command_info.locale), style=discord.ButtonStyle.green)
        async def guess_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != command_info.user.id:
                await interaction.response.send_message(locale.commands.games.flagquiz.notYourGame(command_info.locale), ephemeral=True)
                return
            modal = FlagQuizModal(self.command_info)
            await interaction.response.send_modal(modal)

        @discord.ui.button(label=locale.commands.games.flagquiz.buttons.hint(command_info.locale), style=discord.ButtonStyle.blurple)
        async def hint_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != command_info.user.id:
                await interaction.followup.send(locale.commands.games.flagquiz.notYourGame(command_info.locale), ephemeral=True)
                return
            nonlocal hints_used
            if hints_used == 0:
                hints_used += 1
                await update_game(interaction, hint_used=True)
            else:
                await interaction.followup.send(locale.commands.games.flagquiz.error.hintUsed(command_info.locale), ephemeral=True)

        @discord.ui.button(label=locale.commands.games.flagquiz.buttons.giveUp(command_info.locale), style=discord.ButtonStyle.red)
        async def give_up_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.defer()
            if interaction.user.id != command_info.user.id:
                await interaction.followup.send(locale.commands.games.flagquiz.notYourGame(command_info.locale), ephemeral=True)
                return
            await update_game(interaction, given_up=True)
    view = FlagQuizView(command_info)
    file = discord.File(f'commands/games/country_flags/{flag_file}', filename='flag.png')
    embed = utility.tanjunEmbed(title=locale.commands.games.flagquiz.title(command_info.locale), description=locale.commands.games.flagquiz.initial.description(command_info.locale, guesses=''))
    embed.set_image(url='attachment://flag.png')
    await command_info.reply(view=view, embed=embed, file=file)