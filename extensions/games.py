import discord
from discord.ext import commands
from discord import app_commands
import utility

from commands.games.tic_tac_toe import tic_tac_toe
from commands.games.connect4 import connect4

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

    @app_commands.command(
        name=app_commands.locale_str("connect4_name"),
        description=app_commands.locale_str("connect4_description"),
    )
    @app_commands.choices(
        size=[
            app_commands.Choice(
                value="7,6",
                name=app_commands.locale_str("admin_purge_params_setting_default"),
            ),
            app_commands.Choice(
                value="8,7",
                name=app_commands.locale_str("admin_purge_params_setting_8x7"),
            ),
            app_commands.Choice(
                value="9,8",
                name=app_commands.locale_str("admin_purge_params_setting_9x8"),
            ),
            app_commands.Choice(
                value="10,9",
                name=app_commands.locale_str("admin_purge_params_setting_10x9"),
            ),
            app_commands.Choice(
                value="11,10",
                name=app_commands.locale_str(
                    "admin_purge_params_setting_11x10"
                ),
            ),
            app_commands.Choice(
                value="12,11",
                name=app_commands.locale_str("admin_purge_params_setting_12x11"),
            ),
            app_commands.Choice(
                value="12,12",
                name=app_commands.locale_str("admin_purge_params_setting_12x12"),
            ),
            app_commands.Choice(
                value="4,4",
                name=app_commands.locale_str("admin_purge_params_setting_4x4"),
            ),
        ]
    )
    async def connect4_cmd(self, ctx, user: discord.Member = None, size: app_commands.Choice[str] = "7,6"):
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
        size = size.value.split(",") if size != "7,6" else "7,6".split(",")
        await connect4(commandInfo, ctx.user, user, int(size[0]), int(size[1]))



class gameCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        gameCmds = gameCommands(name="gamecommands", description="Game Commands")
        self.bot.tree.add_command(gameCmds)


async def setup(bot):
    await bot.add_cog(gameCog(bot))
