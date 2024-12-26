# Unused imports:
# from typing import List, Optional
import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.utility.messagetrackingoptout import optOut as optOutCommand
from commands.utility.messagetrackingoptin import optIn as optInCommand
from commands.utility.autopublish import autopublish as autopublishCommand
from commands.utility.autopublish import autopublish_remove as autopublishRemoveCommand
from commands.utility.avatar import avatar as avatarCommand
from commands.utility.banner import banner as bannerCommand
from commands.utility.feedback import feedback as feedbackCommand
from commands.utility.avatarDecoration import (
    avatarDecoration as avatarDecorationCommand,
)
from commands.utility.afk import afk as afkCommand
from commands.utility.claimBoosterRole import (
    claimBoosterRole as claimboosterroleCommand,
)
from commands.utility.deleteBoosterRole import (
    deleteBoosterRole as deleteboosterroleCommand,
)
from commands.utility.setupBoosterRole import (
    setupBoosterRole as setupboosterroleCommand,
)
from commands.utility.claimBoosterChannel import (
    claimBoosterChannel as claimboosterchannelCommand,
)
from commands.utility.deleteBoosterChannel import (
    deleteBoosterChannel as deleteboosterchannelCommand,
)
from commands.utility.setupBoosterChannel import (
    setupBoosterChannel as setupboosterchannelCommand,
)
from commands.utility.schedulemessage import schedule_message as scheduleMessageCommand
from commands.utility.listscheduled import (
    list_scheduled_messages as listScheduledCommand,
)
from commands.utility.removescheduled import (
    remove_scheduled_message as removeScheduledCommand,
)
from commands.utility.report import report as reportCommand
from commands.utility.help import help as helpCommand
from commands.utility.brawlstars.battlelog import battlelog as battlelogCommand
from commands.utility.brawlstars.playerinfo import (
    playerInfo as brawlstarsPlayerInfoCommand,
)
from commands.utility.brawlstars.brawlers import brawlers as brawlstarsBrawlersCommand
from commands.utility.brawlstars.club import club as brawlstarsClubCommand
from commands.utility.brawlstars.events import events as brawlstarsEventsCommand
from commands.utility.twitch.addTwitchLiveNotification import (
    addTwitchLiveNotification as addTwitchLiveNotificationCommand,
)
from commands.utility.twitch.seeTwitchLiveNotifications import (
    seeTwitchLiveNotifications as seeTwitchLiveNotificationsCommand,
)
from commands.utility.brawlstars.link import link as brawlstarsLinkCommand
from commands.utility.brawlstars.unlink import unlink as brawlstarsUnlinkCommand


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
        name=app_commands.locale_str(
            "utility_claimboosterrole_params_name_description"
        ),
        color=app_commands.locale_str(
            "utility_claimboosterrole_params_color_description"
        ),
        icon=app_commands.locale_str(
            "utility_claimboosterrole_params_icon_description"
        ),
    )
    async def claimboosterrole(
        self, ctx, name: str, color: str = None, icon: discord.Attachment = None
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
        await claimboosterroleCommand(
            commandInfo=commandInfo, name=name, color=color, icon=icon
        )

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
        role=app_commands.locale_str(
            "utility_setupboosterrole_params_role_description"
        ),
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
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.boosterroleinfo.info.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.boosterroleinfo.info.description"
            ),
        )
        await commandInfo.reply(embed=embed)


class BoosterChannelCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_claimboosterchannel_name"),
        description=app_commands.locale_str("utility_claimboosterchannel_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str(
            "utility_claimboosterchannel_params_name_description"
        ),
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
    @app_commands.describe(
        category=app_commands.locale_str(
            "utility_setupboosterchannel_params_category_description"
        ),
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
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.boosterchannelinfo.info.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.boosterchannelinfo.info.description",
            ),
        )
        await commandInfo.reply(embed=embed)


class AutoPublishCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_autopublish_name"),
        description=app_commands.locale_str("utility_autopublish_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "utility_autopublish_params_channel_description"
        ),
    )
    async def autopublish(self, ctx, channel: discord.TextChannel = None):
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
        channel=app_commands.locale_str(
            "utility_autopublish_remove_params_channel_description"
        ),
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


class BrawlStarsCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_bs_battlelog_name"),
        description=app_commands.locale_str("utility_bs_battlelog_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_battlelog_params_tag_description"),
    )
    async def battlelog(self, ctx, tag: str = None):
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

        await battlelogCommand(commandInfo=commandInfo, playerTag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_playerinfo_name"),
        description=app_commands.locale_str("utility_bs_playerinfo_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_playerinfo_params_tag_description"),
    )
    async def playerinfo(self, ctx, tag: str = None):
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

        await brawlstarsPlayerInfoCommand(commandInfo=commandInfo, playerTag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_brawlers_name"),
        description=app_commands.locale_str("utility_bs_brawlers_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_brawlers_params_tag_description"),
    )
    async def brawlers(self, ctx, tag: str = None):
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

        await brawlstarsBrawlersCommand(commandInfo=commandInfo, playerTag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_club_name"),
        description=app_commands.locale_str("utility_bs_club_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_club_params_tag_description"),
    )
    async def club(self, ctx, tag: str = None):
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

        await brawlstarsClubCommand(commandInfo=commandInfo, clubTag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_events_name"),
        description=app_commands.locale_str("utility_bs_events_description"),
    )
    async def events(self, ctx):
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

        await brawlstarsEventsCommand(commandInfo=commandInfo)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_link_name"),
        description=app_commands.locale_str("utility_bs_link_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_link_params_tag_description"),
    )
    async def link(self, ctx, tag: str):
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

        await brawlstarsLinkCommand(commandInfo=commandInfo, playerTag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_unlink_name"),
        description=app_commands.locale_str("utility_bs_unlink_description"),
    )
    async def unlink(self, ctx):
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
        await brawlstarsUnlinkCommand(commandInfo=commandInfo)
        return


class TwitchCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_twitch_add_name"),
        description=app_commands.locale_str("utility_twitch_add_description"),
    )
    @app_commands.describe(
        twitchname=app_commands.locale_str("utility_twitch_add_params_twitchname_description"),
        channel=app_commands.locale_str("utility_twitch_add_params_channel_description"),
        notificationmessage=app_commands.locale_str("utility_twitch_add_params_notificationmessage_description"),
    )
    async def add(
        self,
        ctx,
        twitchname: str,
        channel: discord.TextChannel,
        notificationmessage: str = None,
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

        await addTwitchLiveNotificationCommand(
            commandInfo=commandInfo,
            twitch_name=twitchname,
            channel=channel,
            notification_message=notificationmessage,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_twitch_see_name"),
        description=app_commands.locale_str("utility_twitch_see_description"),
    )
    async def see(self, ctx):
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

        await seeTwitchLiveNotificationsCommand(commandInfo=commandInfo)
        return


class utilityCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_avatar_name"),
        description=app_commands.locale_str("utility_avatar_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("utility_avatar_params_user_description"),
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
        user=app_commands.locale_str("utility_banner_params_user_description"),
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
        user=app_commands.locale_str(
            "utility_avatardecoration_params_user_description"
        ),
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
        reason=app_commands.locale_str("utility_afk_params_reason_description"),
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
        user=app_commands.locale_str("utility_report_params_user_description"),
        reason=app_commands.locale_str("utility_report_params_reason_description"),
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
        content=app_commands.locale_str(
            "utility_schedulemessage_params_content_description"
        ),
        sendin=app_commands.locale_str(
            "utility_schedulemessage_params_sendin_description"
        ),
        channel=app_commands.locale_str(
            "utility_schedulemessage_params_channel_description"
        ),
        repeat=app_commands.locale_str(
            "utility_schedulemessage_params_repeat_description"
        ),
    )
    async def schedulemessage(
        self,
        ctx,
        content: str,
        sendin: str,
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

        attachments = (
            []
        )  # [a for a in [attachment1, attachment2, attachment3, attachment4, attachment5,
        #                          attachment6, attachment7, attachment8, attachment9, attachment10] if a is not None]

        await scheduleMessageCommand(
            commandInfo=commandInfo,
            content=content,
            send_in=sendin,
            channel=channel,
            repeat=repeat,
            attachments=attachments or [],
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
        messageid=app_commands.locale_str(
            "utility_removescheduled_params_messageid_description"
        ),
    )
    async def removescheduled(self, ctx, messageid: int):
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

        await removeScheduledCommand(commandInfo=commandInfo, message_id=messageid)


class utilityCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name=app_commands.locale_str("utility_help_name"),
        description=app_commands.locale_str("utility_help_description"),
    )
    async def help_slash(self, ctx):
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

        await helpCommand(commandInfo=commandInfo, ctx=ctx)
        return

    @commands.Cog.listener()
    async def on_ready(self):
        utilityCmds = utilityCommands(
            name=app_commands.locale_str("utilitycmd_name"),
            description=app_commands.locale_str("utilitycmd_description"),
        )
        messageTrackingCmds = MessageTrackingCommands(
            name=app_commands.locale_str("utility_messagetracking_name"),
            description=app_commands.locale_str("utility_messagetracking_description"),
        )
        utilityCmds.add_command(messageTrackingCmds)
        autoPublishCmds = AutoPublishCommands(
            name=app_commands.locale_str("utility_autopublish_name"),
            description=app_commands.locale_str("utility_autopublish_description"),
        )
        utilityCmds.add_command(autoPublishCmds)
        boosterRoleCmds = BoosterRoleCommands(
            name=app_commands.locale_str("utility_boosterrole_name"),
            description=app_commands.locale_str("utility_boosterrole_description"),
        )
        utilityCmds.add_command(boosterRoleCmds)
        boosterChannelCmds = BoosterChannelCommands(
            name=app_commands.locale_str("utility_boosterchannel_name"),
            description=app_commands.locale_str("utility_boosterchannel_description"),
        )
        utilityCmds.add_command(boosterChannelCmds)
        scheduledMessageCmds = ScheduledMessageCommands(
            name=app_commands.locale_str("utility_scheduledmessage_name"),
            description=app_commands.locale_str("utility_scheduledmessage_description"),
        )
        utilityCmds.add_command(scheduledMessageCmds)
        brawlStarsCmds = BrawlStarsCommands(
            name=app_commands.locale_str("utility_bs_name"),
            description=app_commands.locale_str("utility_bs_description"),
        )
        utilityCmds.add_command(brawlStarsCmds)
        twitchCmds = TwitchCommands(
            name=app_commands.locale_str("utility_twitch_name"),
            description=app_commands.locale_str("utility_twitch_description"),
        )
        utilityCmds.add_command(twitchCmds)
        self.bot.tree.add_command(utilityCmds)


async def setup(bot):
    await bot.add_cog(utilityCog(bot))