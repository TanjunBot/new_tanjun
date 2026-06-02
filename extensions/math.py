from __future__ import annotations
from locale_keys import locale as l10n
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.math.calc import calc as calcCommand
from commands.math.calculator import calculator_command
from commands.math.faculty import faculty_command
from commands.math.num2word import num2word as num2word_command
from commands.math.plot_function import plot_function_command
from commands.math.randomnumber import random_number_command

async def num2wordLocaleAutocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    locales = ['en', 'am', 'ar', 'az', 'by', 'ce', 'cy', 'cz', 'de', 'dk', 'en_GB', 'en_IN', 'en_NG', 'es', 'es_CO', 'es_CR', 'es_VE', 'es_GT', 'eu', 'fa', 'fi', 'fr', 'fr_CH', 'fr_BE', 'fr_DZ', 'he', 'hu', 'id', 'is', 'it', 'ja', 'kn', 'ko', 'kz', 'lt', 'lv', 'no', 'pl', 'pt', 'pt_BR', 'sl', 'sr', 'sv', 'ro', 'ru', 'te', 'tg', 'tr', 'th', 'vi', 'nl', 'uk']
    filtered_locales = [locale for locale in locales if current.lower() in locale.lower()]
    return [app_commands.Choice(name=app_commands.locale_str('commands.math.num2word.locales.' + locale), value=locale) for locale in filtered_locales[:25]]

class MathCommands(discord.app_commands.Group):

    @app_commands.command(name=l10n.math.calc.name.discord_key, description=l10n.math.calc.description.discord_key)
    @app_commands.describe(expression=l10n.math.calc.params.expression.description.discord_key)
    async def calc(self, interaction: discord.Interaction, expression: app_commands.Range[str, 1, 128]) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await calcCommand(command_info=command_info, expression=expression)

    @app_commands.command(name=l10n.math.calculator.name.discord_key, description=l10n.math.calculator.description.discord_key)
    @app_commands.describe(equation=l10n.math.calculator.params.equation.description.discord_key)
    async def calculator(self, interaction: discord.Interaction, equation: app_commands.Range[str, 1, 128]='') -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await calculator_command(command_info, equation)

    @app_commands.command(name=l10n.math.num2word.name.discord_key, description=l10n.math.num2word.description.discord_key)
    @app_commands.describe(number=l10n.math.num2word.params.number.description.discord_key, locale=l10n.math.num2word.params.locale.description.discord_key)
    @app_commands.autocomplete(locale=num2wordLocaleAutocomplete)
    async def num2word(self, interaction: discord.Interaction, number: int, locale: str | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if locale is None:
            locale = str(interaction.locale)
        await num2word_command(command_info, number, locale)

    @app_commands.command(name=l10n.math.randomnumber.name.discord_key, description=l10n.math.randomnumber.description.discord_key)
    @app_commands.describe(min=l10n.math.randomnumber.params.min.description.discord_key, max=l10n.math.randomnumber.params.max.description.discord_key, amount=l10n.math.randomnumber.params.amount.description.discord_key)
    async def random_number(self, interaction: discord.Interaction, min: int, max: int, amount: app_commands.Range[int, 1, 10]=1) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await random_number_command(command_info, min, max, amount)

    @app_commands.command(name=l10n.math.plotfunction.name.discord_key, description=l10n.math.plotfunction.description.discord_key)
    @app_commands.describe(func=l10n.math.plotfunction.params.func.description.discord_key, xmin=l10n.math.plotfunction.params.xmin.description.discord_key, xmax=l10n.math.plotfunction.params.xmax.description.discord_key)
    async def plot_function(self, interaction: discord.Interaction, func: str, xmin: float | None=None, xmax: float | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await plot_function_command(command_info, func, xmin, xmax)

    @app_commands.command(name=l10n.math.faculty.name.discord_key, description=l10n.math.faculty.description.discord_key)
    @app_commands.describe(number=l10n.math.faculty.params.number.description.discord_key)
    async def faculty(self, interaction: discord.Interaction, number: app_commands.Range[int, 0, 100]) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.user.guild_permissions, reply=interaction.followup.send, client=interaction.client)
        await faculty_command(command_info, number)

class MathCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        mathcmds = MathCommands(name=l10n.math.name.discord_key, description=l10n.math.description.discord_key)
        if self.bot.tree:
            self.bot.tree.add_command(mathcmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MathCog(bot))