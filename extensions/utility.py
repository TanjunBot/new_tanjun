import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.utility.messagetrackingoptout import optOut as optOutCommand
from commands.utility.messagetrackingoptin import optIn as optInCommand
from commands.utility.autopublish import autopublish as autopublishCommand
from commands.utility.autopublish import autopublish_remove as autopublishRemoveCommand
from commands.utility.avatar import avatar as avatarCommand
from commands.utility.banner import banner as bannerCommand

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

class AutoPublishCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_autopublish_name"),
        description=app_commands.locale_str("utility_autopublish_description"),
    )
    @app_commands.describe(
        channel="The channel to autopublish messages in.",
    )
    async def autopublish(self, ctx, channel: discord.TextChannel= None):
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

        if not channel:
            channel = ctx.channel

        await autopublishCommand(commandInfo=commandInfo, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("utility_autopublish_remove_name"),
        description=app_commands.locale_str("utility_autopublish_remove_description"),
    )
    @app_commands.describe(
        channel="The channel to remove from autopublishing.",
    )
    async def autopublish_remove(self, ctx, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await autopublishRemoveCommand(commandInfo=commandInfo, channel=channel)

class utilityCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_avatar_name"),
        description=app_commands.locale_str("utility_avatar_description"),
    )
    @app_commands.describe(
        user="The user to get the avatar of.",
    )
    async def avatar(self, ctx, user: discord.Member = None):
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

        if not user:
            user = ctx.user

        await avatarCommand(commandInfo=commandInfo, user=user)

    @app_commands.command(
        name=app_commands.locale_str("utility_banner_name"),
        description=app_commands.locale_str("utility_banner_description"),
    )
    @app_commands.describe(
        user="The user to get the banner of.",
    )
    async def banner(self, ctx, user: discord.Member = None):
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

        if not user:
            user = ctx.user

        await bannerCommand(commandInfo=commandInfo, user=user)

class utilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = utilityCommands(name="utilitycmd", description="Utility Commands")
        messageTrackingCmds = MessageTrackingCommands(name=app_commands.locale_str("utility_messagetracking_name"), description=app_commands.locale_str("utility_messagetracking_description"))
        utilityCmds.add_command(messageTrackingCmds)
        autoPublishCmds = AutoPublishCommands(name=app_commands.locale_str("utility_autopublish_name"), description=app_commands.locale_str("utility_autopublish_description"))
        utilityCmds.add_command(autoPublishCmds)
        self.bot.tree.add_command(utilityCmds)


async def setup(bot):
    await bot.add_cog(utilityCog(bot))
