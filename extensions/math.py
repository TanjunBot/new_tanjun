import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List

from commands.math.calc import calc as calcCommand
from commands.math.calculator import calculator_command
from commands.math.num2word import num2word as num2word_command


async def num2wordLocaleAutocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    locales = [
        "en",
        "am",
        "ar",
        "az",
        "by",
        "ce",
        "cy",
        "cz",
        "de",
        "dk",
        "en_GB",
        "en_IN",
        "en_NG",
        "es",
        "es_CO",
        "es_CR",
        "es_VE",
        "es_GT",
        "eu",
        "fa",
        "fi",
        "fr",
        "fr_CH",
        "fr_BE",
        "fr_DZ",
        "he",
        "hu",
        "id",
        "is",
        "it",
        "ja",
        "kn",
        "ko",
        "kz",
        "lt",
        "lv",
        "no",
        "pl",
        "pt",
        "pt_BR",
        "sl",
        "sr",
        "sv",
        "ro",
        "ru",
        "te",
        "tg",
        "tr",
        "th",
        "vi",
        "nl",
        "uk",
    ]

    filtered_locales = [
        locale
        for locale in locales
        if current.lower() in locale.lower()
    ]

    return [
        app_commands.Choice(name=locale, value=locale)
        for locale in filtered_locales[:25]
    ]


class mathCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("math_calc_name"),
        description=app_commands.locale_str("math_calc_description"),
    )
    @app_commands.describe(
        expression=app_commands.locale_str("math_calc_params_expression_description"),
    )
    async def calc(self, ctx, expression: str):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await calcCommand(commandInfo=commandInfo, expression=expression)

    @app_commands.command(
        name=app_commands.locale_str("math_calculator_name"),
        description=app_commands.locale_str("math_calculator_description"),
    )
    @app_commands.describe(
        equation=app_commands.locale_str("math_calculator_params_equation_description"),
    )
    async def calculator(self, ctx, equation: str = ""):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await calculator_command(commandInfo, equation)
    

    @app_commands.command(
        name=app_commands.locale_str("math_num2word_name"),
        description=app_commands.locale_str("math_num2word_description"),
    )
    @app_commands.describe(
        number=app_commands.locale_str("math_num2word_params_number_description"),
        locale=app_commands.locale_str("math_num2word_params_locale_description"),
    )
    @app_commands.autocomplete(locale=num2wordLocaleAutocomplete)
    async def num2word(self, ctx, number: int, locale: str = None):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if locale is None:
            locale = str(ctx.locale)


        await num2word_command(commandInfo, number, locale)


class mathCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def calc(self, ctx, expression: str):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.send,
            client=ctx.bot,
        )

        await calcCommand(commandInfo=commandInfo, expression=expression)

    @commands.command()
    async def calculator(self, ctx, *, equation: str = ""):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.send,
            client=ctx.bot,
        )
        await calculator_command(commandInfo, equation)

    @commands.command()
    async def num2word(self, ctx, number: int, locale: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.send,
            client=ctx.bot,
        )

        if locale is None:
            locale = ctx.locale

        await num2word_command(commandInfo, number, locale)

    @commands.Cog.listener()
    async def on_ready(self):
        mathcmds = mathCommands(name="math", description="Math is fun!")
        self.bot.tree.add_command(mathcmds)


async def setup(bot):
    await bot.add_cog(mathCog(bot))
