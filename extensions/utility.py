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
from commands.utility.feedback import feedback as feedbackCommand
from commands.utility.avatarDecoration import avatarDecoration as avatarDecorationCommand
from commands.utility.afk import afk as afkCommand
from commands.utility.claimBoosterRole import claimBoosterRole as claimboosterroleCommand
from commands.utility.deleteBoosterRole import deleteBoosterRole as deleteboosterroleCommand
from commands.utility.setupBoosterRole import setupBoosterRole as setupboosterroleCommand
from commands.utility.claimBoosterChannel import claimBoosterChannel as claimboosterchannelCommand
from commands.utility.deleteBoosterChannel import deleteBoosterChannel as deleteboosterchannelCommand
from commands.utility.setupBoosterChannel import setupBoosterChannel as setupboosterchannelCommand
from commands.utility.schedulemessage import schedule_message as scheduleMessageCommand
from commands.utility.listscheduled import list_scheduled_messages as listScheduledCommand
from commands.utility.removescheduled import remove_scheduled_message as removeScheduledCommand
from commands.utility.report import report as reportCommand

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

class BoosterRoleCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_claimboosterrole_name"),
        description=app_commands.locale_str("utility_claimboosterrole_description"),
    )
    @app_commands.describe(
        name="The name of the booster role.",
        color="The color of the booster role.",
        icon="The icon of the booster role.",
    )
    async def claimboosterrole(self, ctx, name: str, color: str = None, icon: discord.Attachment = None):
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
        await claimboosterroleCommand(commandInfo=commandInfo, name=name, color=color, icon=icon)

    @app_commands.command(
        name=app_commands.locale_str("utility_deleteboosterrole_name"),
        description=app_commands.locale_str("utility_deleteboosterrole_description"),
    )
    async def deleteboosterrole(self, ctx):
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
        await deleteboosterroleCommand(commandInfo=commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("utility_setupboosterrole_name"),
        description=app_commands.locale_str("utility_setupboosterrole_description"),
    )
    @app_commands.describe(
        role="The base role. This will be copied to create the booster role.",
    )
    async def setupboosterrole(self, ctx, role: discord.Role):
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
        await setupboosterroleCommand(commandInfo=commandInfo, role=role)

    @app_commands.command(
        name=app_commands.locale_str("utility_boosterroleinfo_name"),
        description=app_commands.locale_str("utility_boosterroleinfo_description"),
    )
    async def info(self, ctx):
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

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.boosterroleinfo.info.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.boosterroleinfo.info.description"),
        )
        await commandInfo.reply(embed=embed)

class BoosterChannelCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_claimboosterchannel_name"),
        description=app_commands.locale_str("utility_claimboosterchannel_description"),
    )
    @app_commands.describe(
        name="The name of the booster channel.",
    )
    async def claimboosterchannel(self, ctx, name: str):
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
        await claimboosterchannelCommand(commandInfo=commandInfo, name=name)

    @app_commands.command(
        name=app_commands.locale_str("utility_deleteboosterch_name"),
        description=app_commands.locale_str("utility_deleteboosterchannel_description"),
    )
    async def deleteboosterchannel(self, ctx):
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
        await deleteboosterchannelCommand(commandInfo=commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("utility_setupboosterchannel_name"),
        description=app_commands.locale_str("utility_setupboosterchannel_description"),
    )
    async def setupboosterchannel(self, ctx, category: discord.CategoryChannel):
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
        await setupboosterchannelCommand(commandInfo=commandInfo, category=category)
    
    @app_commands.command(
        name=app_commands.locale_str("utility_boosterchannelinfo_name"),
        description=app_commands.locale_str("utility_boosterchannelinfo_description"),
    )
    async def info(self, ctx):
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

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.boosterchannelinfo.info.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.boosterchannelinfo.info.description"),
        )
        await commandInfo.reply(embed=embed)

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

    @app_commands.command(
        name=app_commands.locale_str("utility_avatardecoration_name"),
        description=app_commands.locale_str("utility_avatardecoration_description"),
    )
    @app_commands.describe(
        user="The user to get the avatar decoration of.",
    )
    async def avatardecoration(self, ctx, user: discord.Member = None):
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

        await avatarDecorationCommand(commandInfo=commandInfo, user=user)

    @app_commands.command(
        name=app_commands.locale_str("utility_feedback_name"),
        description=app_commands.locale_str("utility_feedback_description"),
    )
    async def feedback(self, ctx):
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.response.send_message,
            client=ctx.client,
        )

        await feedbackCommand(commandInfo=commandInfo, ctx=ctx)

    @app_commands.command(
        name=app_commands.locale_str("utility_afk_name"),
        description=app_commands.locale_str("utility_afk_description"),
    )
    @app_commands.describe(
        reason="The reason for being afk.",
    )
    async def afk(self, ctx, reason: app_commands.Range[str, 0, 1000]):
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

        await afkCommand(commandInfo=commandInfo, reason=reason)

    @app_commands.command(
        name=app_commands.locale_str("utility_report_name"),
        description=app_commands.locale_str("utility_report_description"),
    )
    @app_commands.describe(
        user="The user to report.",
        reason="The reason for reporting the user.",
    )
    async def report(self, ctx, user: discord.Member, reason: str):
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
        await reportCommand(commandInfo=commandInfo, user=user, reason=reason)


class ScheduledMessageCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_schedulemessage_name"),
        description=app_commands.locale_str("utility_schedulemessage_description"),
    )
    @app_commands.describe(
        content="The message content to schedule",
        send_in="When to send the message (e.g. '1h', '2d', '30m')",
        channel="The channel to send the message in (optional)",
        repeat="How often to repeat the message (e.g. '1h', '1d') (optional)",
    )
    async def schedulemessage(
        self, 
        ctx, 
        content: str,
        send_in: str,
        channel: discord.TextChannel = None,
        repeat: str = None,
        # attachment1: discord.Attachment = None,
        # attachment2: discord.Attachment = None,
        # attachment3: discord.Attachment = None,
        # attachment4: discord.Attachment = None,
        # attachment5: discord.Attachment = None,
        # attachment6: discord.Attachment = None,
        # attachment7: discord.Attachment = None,
        # attachment8: discord.Attachment = None,
        # attachment9: discord.Attachment = None,
        # attachment10: discord.Attachment = None,
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

        attachments = [] # [a for a in [attachment1, attachment2, attachment3, attachment4, attachment5,
        #                          attachment6, attachment7, attachment8, attachment9, attachment10] if a is not None]
        
        await scheduleMessageCommand(
            commandInfo=commandInfo,
            content=content,
            send_in=send_in,
            channel=channel,
            repeat=repeat,
            attachments=attachments or []
        )

    @app_commands.command(
        name=app_commands.locale_str("utility_listscheduled_name"),
        description=app_commands.locale_str("utility_listscheduled_description"),
    )
    async def listscheduled(self, ctx):
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
        
        await listScheduledCommand(commandInfo=commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("utility_removescheduled_name"),
        description=app_commands.locale_str("utility_removescheduled_description"),
    )
    @app_commands.describe(
        message_id="The ID of the scheduled message to remove",
    )
    async def removescheduled(self, ctx, message_id: int):
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
        
        await removeScheduledCommand(commandInfo=commandInfo, message_id=message_id)

class utilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description="Get help with the bot"
    )
    async def help_slash(self, ctx):
        await ctx.response.send_message("ima help you!")

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = utilityCommands(name="utilitycmd", description="Utility Commands")
        messageTrackingCmds = MessageTrackingCommands(name=app_commands.locale_str("utility_messagetracking_name"), description=app_commands.locale_str("utility_messagetracking_description"))
        utilityCmds.add_command(messageTrackingCmds)
        autoPublishCmds = AutoPublishCommands(name=app_commands.locale_str("utility_autopublish_name"), description=app_commands.locale_str("utility_autopublish_description"))
        utilityCmds.add_command(autoPublishCmds)
        boosterRoleCmds = BoosterRoleCommands(name=app_commands.locale_str("utility_boosterrole_name"), description=app_commands.locale_str("utility_boosterrole_description"))
        utilityCmds.add_command(boosterRoleCmds)
        boosterChannelCmds = BoosterChannelCommands(name=app_commands.locale_str("utility_boosterchannel_name"), description=app_commands.locale_str("utility_boosterchannel_description"))
        utilityCmds.add_command(boosterChannelCmds)
        scheduledMessageCmds = ScheduledMessageCommands(name=app_commands.locale_str("utility_scheduledmessage_name"), description=app_commands.locale_str("utility_scheduledmessage_description"))
        utilityCmds.add_command(scheduledMessageCmds)
        self.bot.tree.add_command(utilityCmds)


async def setup(bot):
    await bot.add_cog(utilityCog(bot))
