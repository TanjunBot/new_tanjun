import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.utility.messagetrackingoptout import optOut as optOutCommand

class utilityCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_messageoptout_name"),
        description=app_commands.locale_str("utility_messageoptout_description"),
    )
    async def messagetrackingoptout(self, ctx):
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

        await optOutCommand(commandInfo=commandInfo)


class utilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = utilityCommands(name="utilitycmd", description="Utility Commands")
        self.bot.tree.add_command(utilityCmds)

    


async def setup(bot):
    await bot.add_cog(utilityCog(bot))
