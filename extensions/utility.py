import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.utility.messagetrackingoptout import optOut as optOutCommand
from commands.utility.messagetrackingoptin import optIn as optInCommand

class MessageTrackingCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_messageoptout_name"),
        description=app_commands.locale_str("utility_messageoptout_description"),
    )
    async def messagetrackingoptout(self, ctx):
        await ctx.response.defer(ephemeral=True)
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

    @app_commands.command(
        name=app_commands.locale_str("utility_messageoptin_name"),
        description=app_commands.locale_str("utility_messageoptin_description"),
    )
    async def messagetrackingoptin(self, ctx):
        await ctx.response.defer(ephemeral=True)
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

        await optInCommand(commandInfo=commandInfo)

class utilityCommands(discord.app_commands.Group):
    ...


class utilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = utilityCommands(name="utilitycmd", description="Utility Commands")
        messageTrackingCmds = MessageTrackingCommands(name=app_commands.locale_str("utility_messagetracking_name"), description=app_commands.locale_str("utility_messagetracking_description"))
        utilityCmds.add_command(messageTrackingCmds)
        self.bot.tree.add_command(utilityCmds)


async def setup(bot):
    await bot.add_cog(utilityCog(bot))
