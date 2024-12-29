# Unused imports:
# from localizer import tanjunLocalizer
import discord
from discord.ext import commands
from discord import app_commands
import utility
from typing import List  # , Optional

from commands.math.calc import calc as calcCommand
from commands.math.calculator import calculator_command
from commands.math.num2word import num2word as num2word_command
from commands.math.randomnumber import random_number_command
from commands.math.plot_function import plot_function_command
from commands.math.faculty import faculty_command


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
        locale for locale in locales if current.lower() in locale.lower()
    ]

    return [
        app_commands.Choice(
            name=app_commands.locale_str("commands.math.num2word.locales." + locale),
            value=locale,
        )
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
    async def calc(self, ctx, expression: app_commands.Range[str, 1, 128]):
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
    async def calculator(self, ctx, equation: app_commands.Range[str, 1, 128] = ""):
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

    @app_commands.command(
        name=app_commands.locale_str("math_randomnumber_name"),
        description=app_commands.locale_str("math_randomnumber_description"),
    )
    @app_commands.describe(
        min=app_commands.locale_str("math_randomnumber_params_min_description"),
        max=app_commands.locale_str("math_randomnumber_params_max_description"),
        amount=app_commands.locale_str("math_randomnumber_params_amount_description"),
    )
    async def random_number(
        self, ctx, min: int, max: int, amount: app_commands.Range[int, 1, 10] = 1
    ):
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

        await random_number_command(commandInfo, min, max, amount)

    @app_commands.command(
        name=app_commands.locale_str("math_plotfunction_name"),
        description=app_commands.locale_str("math_plotfunction_description"),
    )
    @app_commands.describe(
        func=app_commands.locale_str("math_plotfunction_params_func_description"),
        xmin=app_commands.locale_str("math_plotfunction_params_xmin_description"),
        xmax=app_commands.locale_str("math_plotfunction_params_xmax_description"),
    )
    async def plot_function(
        self, ctx, func: str, xmin: float = None, xmax: float = None
    ):
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

        await plot_function_command(commandInfo, func, xmin, xmax)

    @app_commands.command(
        name=app_commands.locale_str("math_faculty_name"),
        description=app_commands.locale_str("math_faculty_description"),
    )
    @app_commands.describe(
        number=app_commands.locale_str("math_faculty_params_number_description"),
    )
    async def faculty(self, ctx, number: app_commands.Range[int, 0, 100]):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.user.guild_permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await faculty_command(commandInfo, number)


class mathCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        mathcmds = mathCommands(
            name=app_commands.locale_str("math_name"),
            description=app_commands.locale_str("math_description"),
        )
        self.bot.tree.add_command(mathcmds)


async def setup(bot):
    await bot.add_cog(mathCog(bot))
