import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.math.calc import calc as calcCommand
from commands.math.calculator import calculator_command

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

    @commands.Cog.listener()
    async def on_ready(self):
        mathcmds = mathCommands(
            name="math", description="Math is fun!"
        )
        self.bot.tree.add_command(mathcmds)



async def setup(bot):
    await bot.add_cog(mathCog(bot))
