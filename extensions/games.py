import discord
from discord.ext import commands
from discord import app_commands
import utility

from commands.games.tic_tac_toe import tic_tac_toe

class gameCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("ttt_name"),
        description=app_commands.locale_str("ttt_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("ttt_user_description"),
    )
    async def tic_tac_toe_cmd(self, ctx, user: discord.Member = None):
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
        await tic_tac_toe(commandInfo, ctx.user, user)


class gameCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        gameCmds = gameCommands(name="gamecommands", description="Game Commands")
        self.bot.tree.add_command(gameCmds)


async def setup(bot):
    await bot.add_cog(gameCog(bot))
