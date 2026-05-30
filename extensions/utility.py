
import discord
from discord import app_commands
from discord.ext import commands

import utility
from commands.utility.afk import afk as afkCommand
from commands.utility.autopublish import autopublish as autopublishCommand
from commands.utility.autopublish import autopublish_remove as autopublishRemoveCommand
from commands.utility.avatar import avatar as avatarCommand
from commands.utility.avatar_decoration import (
    avatarDecoration as avatarDecorationCommand,
)
from commands.utility.banner import banner as bannerCommand
from commands.utility.brawlstars.battlelog import battlelog as battlelogCommand
from commands.utility.brawlstars.brawlers import brawlers as brawlstarsBrawlersCommand
from commands.utility.brawlstars.club import club as brawlstarsClubCommand
from commands.utility.brawlstars.events import events as brawlstarsEventsCommand
from commands.utility.brawlstars.link import link as brawlstarsLinkCommand
from commands.utility.brawlstars.playerinfo import (
    player_info as brawlstarsPlayerInfoCommand,
)
from commands.utility.brawlstars.unlink import unlink as brawlstarsUnlinkCommand
from commands.utility.claim_booster_channel import (
    claimBoosterChannel as claimboosterchannelCommand,
)
from commands.utility.claim_booster_role import (
    claimBoosterRole as claimboosterroleCommand,
)
from commands.utility.delete_booster_channel import (
    deleteBoosterChannel as deleteboosterchannelCommand,
)
from commands.utility.delete_booster_role import (
    deleteBoosterRole as deleteboosterroleCommand,
)
from commands.utility.feedback import feedback as feedbackCommand
from commands.utility.help import help as helpCommand
from commands.utility.listscheduled import (
    list_scheduled_messages as listScheduledCommand,
)
from commands.utility.messagetrackingoptin import optIn as optInCommand
from commands.utility.messagetrackingoptout import optOut as optOutCommand
from commands.utility.removescheduled import (
    remove_scheduled_message as removeScheduledCommand,
)
from commands.utility.report import report as reportCommand
from commands.utility.schedulemessage import schedule_message as scheduleMessageCommand
from commands.utility.setup_booster_channel import (
    setupBoosterChannel as setupboosterchannelCommand,
)
from commands.utility.setup_booster_role import (
    setupBoosterRole as setupboosterroleCommand,
)
from commands.utility.twitch.add_twitch_live_notification import (
    addTwitchLiveNotification as addTwitchLiveNotificationCommand,
)
from commands.utility.twitch.see_twitch_live_notifications import (
    seeTwitchLiveNotifications as seeTwitchLiveNotificationsCommand,
)
from localizer import tanjunLocalizer
from utility import EmbedColor


class MessageTrackingCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_messageoptout_name"),
        description=app_commands.locale_str("utility_messageoptout_description"),
    )
    async def messagetrackingoptout(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast

        command_info = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,  # type: ignore[arg-type]
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await optOutCommand(command_info=command_info)

    @app_commands.command(
        name=app_commands.locale_str("utility_messageoptin_name"),
        description=app_commands.locale_str("utility_messageoptin_description"),
    )
    async def messagetrackingoptin(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast

        command_info = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,  # type: ignore[arg-type]
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await optInCommand(command_info=command_info)


class BoosterRoleCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_claimboosterrole_name"),
        description=app_commands.locale_str("utility_claimboosterrole_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("utility_claimboosterrole_params_name_description"),
        color=app_commands.locale_str("utility_claimboosterrole_params_color_description"),
        icon=app_commands.locale_str("utility_claimboosterrole_params_icon_description"),
    )
    async def claimboosterrole(  # type: ignore[no-untyped-def]
        self,
        ctx,
        name: app_commands.Range[str, 1, 100],
        color: app_commands.Range[str, 6, 7] = None,  # type: ignore[assignment]
        icon: discord.Attachment = None,  # type: ignore[assignment]
    ) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await claimboosterroleCommand(command_info=command_info, name=name, color=color, icon=icon)

    @app_commands.command(
        name=app_commands.locale_str("utility_deleteboosterrole_name"),
        description=app_commands.locale_str("utility_deleteboosterrole_description"),
    )
    async def deleteboosterrole(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await deleteboosterroleCommand(command_info=command_info)

    @app_commands.command(
        name=app_commands.locale_str("utility_setupboosterrole_name"),
        description=app_commands.locale_str("utility_setupboosterrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("utility_setupboosterrole_params_role_description"),
    )
    async def setupboosterrole(self, ctx, role: discord.Role) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await setupboosterroleCommand(command_info=command_info, role=role)

    @app_commands.command(
        name=app_commands.locale_str("utility_boosterroleinfo_name"),
        description=app_commands.locale_str("utility_boosterroleinfo_description"),
    )
    async def info(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
            colour=EmbedColor.INFO,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.boosterroleinfo.info.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.boosterroleinfo.info.description"),
        )
        await command_info.reply(embed=embed)


class BoosterChannelCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_claimboosterchannel_name"),
        description=app_commands.locale_str("utility_claimboosterchannel_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("utility_claimboosterchannel_params_name_description"),
    )
    async def claimboosterchannel(self, ctx, name: app_commands.Range[str, 1, 100]) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await claimboosterchannelCommand(command_info=command_info, name=name)

    @app_commands.command(
        name=app_commands.locale_str("utility_deleteboosterch_name"),
        description=app_commands.locale_str("utility_deleteboosterchannel_description"),
    )
    async def deleteboosterchannel(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await deleteboosterchannelCommand(command_info=command_info)

    @app_commands.command(
        name=app_commands.locale_str("utility_setupboosterchannel_name"),
        description=app_commands.locale_str("utility_setupboosterchannel_description"),
    )
    @app_commands.describe(
        category=app_commands.locale_str("utility_setupboosterchannel_params_category_description"),
    )
    async def setupboosterchannel(self, ctx, category: discord.CategoryChannel) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await setupboosterchannelCommand(command_info=command_info, category=category)

    @app_commands.command(
        name=app_commands.locale_str("utility_boosterchannelinfo_name"),
        description=app_commands.locale_str("utility_boosterchannelinfo_description"),
    )
    async def info(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
            colour=EmbedColor.INFO,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.boosterchannelinfo.info.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.boosterchannelinfo.info.description",
            ),
        )
        await command_info.reply(embed=embed)


class AutoPublishCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_autopublish_name"),
        description=app_commands.locale_str("utility_autopublish_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("utility_autopublish_params_channel_description"),
    )
    async def autopublish(self, ctx, channel: discord.TextChannel = None) -> None:  # type: ignore[no-untyped-def, assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = ctx.channel

        await autopublishCommand(command_info=command_info, channel=channel)

    @app_commands.command(
        name=app_commands.locale_str("utility_autopublish_remove_name"),
        description=app_commands.locale_str("utility_autopublish_remove_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("utility_autopublish_remove_params_channel_description"),
    )
    async def autopublish_remove(self, ctx, channel: discord.TextChannel = None) -> None:  # type: ignore[no-untyped-def, assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = ctx.channel

        await autopublishRemoveCommand(command_info=command_info, channel=channel)


class BrawlStarsCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_bs_battlelog_name"),
        description=app_commands.locale_str("utility_bs_battlelog_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_battlelog_params_tag_description"),
    )
    async def battlelog(self, ctx, tag: str | None = None) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await battlelogCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_playerinfo_name"),
        description=app_commands.locale_str("utility_bs_playerinfo_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_playerinfo_params_tag_description"),
    )
    async def playerinfo(self, ctx, tag: str | None = None) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await brawlstarsPlayerInfoCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_brawlers_name"),
        description=app_commands.locale_str("utility_bs_brawlers_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_brawlers_params_tag_description"),
    )
    async def brawlers(self, ctx, tag: str | None = None) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await brawlstarsBrawlersCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_club_name"),
        description=app_commands.locale_str("utility_bs_club_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_club_params_tag_description"),
    )
    async def club(self, ctx, tag: str) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await brawlstarsClubCommand(command_info=command_info, club_tag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_events_name"),
        description=app_commands.locale_str("utility_bs_events_description"),
    )
    async def events(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await brawlstarsEventsCommand(command_info=command_info)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_link_name"),
        description=app_commands.locale_str("utility_bs_link_description"),
    )
    @app_commands.describe(
        tag=app_commands.locale_str("utility_bs_link_params_tag_description"),
    )
    async def link(self, ctx, tag: str) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await brawlstarsLinkCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_bs_unlink_name"),
        description=app_commands.locale_str("utility_bs_unlink_description"),
    )
    async def unlink(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
        await brawlstarsUnlinkCommand(command_info=command_info)
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
    async def add(  # type: ignore[no-untyped-def]
        self,
        ctx,
        twitchname: str,
        channel: discord.TextChannel,
        notificationmessage: app_commands.Range[str, 0, 1024] = None,  # type: ignore[assignment]
    ) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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
            command_info=command_info,
            twitch_name=twitchname,
            channel=channel,
            notification_message=notificationmessage,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("utility_twitch_see_name"),
        description=app_commands.locale_str("utility_twitch_see_description"),
    )
    async def see(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await seeTwitchLiveNotificationsCommand(command_info=command_info)
        return


class UtilityCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_avatar_name"),
        description=app_commands.locale_str("utility_avatar_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("utility_avatar_params_user_description"),
    )
    async def avatar(self, ctx, user: discord.Member = None) -> None:  # type: ignore[no-untyped-def, assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        if not user:  # type: ignore[truthy-bool]
            user = ctx.user

        await avatarCommand(command_info=command_info, user=user)

    @app_commands.command(
        name=app_commands.locale_str("utility_banner_name"),
        description=app_commands.locale_str("utility_banner_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("utility_banner_params_user_description"),
    )
    async def banner(self, ctx, user: discord.Member = None) -> None:  # type: ignore[no-untyped-def, assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        if not user:  # type: ignore[truthy-bool]
            user = ctx.user

        await bannerCommand(command_info=command_info, user=user)  # type: ignore[arg-type]

    @app_commands.command(
        name=app_commands.locale_str("utility_avatardecoration_name"),
        description=app_commands.locale_str("utility_avatardecoration_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("utility_avatardecoration_params_user_description"),
    )
    async def avatardecoration(self, ctx, user: discord.Member = None) -> None:  # type: ignore[no-untyped-def, assignment]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        if not user:  # type: ignore[truthy-bool]
            user = ctx.user

        await avatarDecorationCommand(command_info=command_info, user=user)

    @app_commands.command(
        name=app_commands.locale_str("utility_feedback_name"),
        description=app_commands.locale_str("utility_feedback_description"),
    )
    async def feedback(self, ctx) -> None:  # type: ignore[no-untyped-def]
        command_info = utility.CommandInfo(
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

        await feedbackCommand(command_info=command_info, ctx=ctx)

    @app_commands.command(
        name=app_commands.locale_str("utility_afk_name"),
        description=app_commands.locale_str("utility_afk_description"),
    )
    @app_commands.describe(
        reason=app_commands.locale_str("utility_afk_params_reason_description"),
    )
    async def afk(self, ctx, reason: app_commands.Range[str, 0, 1000]) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await afkCommand(command_info=command_info, reason=reason)

    @app_commands.command(
        name=app_commands.locale_str("utility_report_name"),
        description=app_commands.locale_str("utility_report_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("utility_report_params_user_description"),
        reason=app_commands.locale_str("utility_report_params_reason_description"),
        attachment=app_commands.locale_str("utility_report_params_attachment_description"),
        anonymous=app_commands.locale_str("utility_report_params_anonymous_description"),
    )
    async def report(
        self,
        ctx,
        user: discord.Member,
        reason: app_commands.Range[str, 12, 1024],  # type: ignore[no-untyped-def]
        attachment: discord.Attachment | None = None,
        anonymous: bool = False,
    ) -> None:
        await ctx.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(
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
        await reportCommand(
            command_info=command_info,
            user=user,
            reason=reason,
            attachment=attachment,
            anonymous=anonymous,
        )


class ScheduledMessageCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("utility_schedulemessage_name"),
        description=app_commands.locale_str("utility_schedulemessage_description"),
    )
    @app_commands.describe(
        content=app_commands.locale_str("utility_schedulemessage_params_content_description"),
        sendin=app_commands.locale_str("utility_schedulemessage_params_sendin_description"),
        channel=app_commands.locale_str("utility_schedulemessage_params_channel_description"),
        repeatinterval=app_commands.locale_str("utility_schedulemessage_params_repeat_description"),
        repeatamount=app_commands.locale_str("utility_schedulemessage_params_repeatamount_description"),
        attachment1=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment2=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment3=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment4=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment5=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment6=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment7=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment8=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment9=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
        attachment10=app_commands.locale_str("utility_schedulemessage_params_attachment_description"),
    )
    async def schedulemessage(  # type: ignore[no-untyped-def]
        self,
        ctx,
        content: app_commands.Range[str, 1, 1024],
        sendin: app_commands.Range[str, 1, 100],
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        repeatinterval: app_commands.Range[str, 0, 15] = None,  # type: ignore[assignment]
        repeatamount: app_commands.Range[int, 0, 1000] = None,  # type: ignore[assignment]
        attachment1: discord.Attachment = None,  # type: ignore[assignment]
        attachment2: discord.Attachment = None,  # type: ignore[assignment]
        attachment3: discord.Attachment = None,  # type: ignore[assignment]
        attachment4: discord.Attachment = None,  # type: ignore[assignment]
        attachment5: discord.Attachment = None,  # type: ignore[assignment]
        attachment6: discord.Attachment = None,  # type: ignore[assignment]
        attachment7: discord.Attachment = None,  # type: ignore[assignment]
        attachment8: discord.Attachment = None,  # type: ignore[assignment]
        attachment9: discord.Attachment = None,  # type: ignore[assignment]
        attachment10: discord.Attachment = None,  # type: ignore[assignment]
    ) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        attachments: list[discord.Attachment] = [a for a in [attachment1, attachment2, attachment3, attachment4, attachment5,
                                                             attachment6, attachment7, attachment8, attachment9, attachment10] if a is not None]

        await scheduleMessageCommand(
            command_info=command_info,
            content=content,
            send_in=sendin,
            channel=channel,
            repeat=repeatinterval,
            repeat_amount=repeatamount,
            attachments=attachments or [],
        )

    @app_commands.command(
        name=app_commands.locale_str("utility_listscheduled_name"),
        description=app_commands.locale_str("utility_listscheduled_description"),
    )
    async def listscheduled(self, ctx) -> None:  # type: ignore[no-untyped-def]
        await ctx.response.defer()
        command_info = utility.CommandInfo(
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

        await listScheduledCommand(command_info=command_info)

    @app_commands.command(
        name=app_commands.locale_str("utility_removescheduled_name"),
        description=app_commands.locale_str("utility_removescheduled_description"),
    )
    @app_commands.describe(
        messageid=app_commands.locale_str("utility_removescheduled_params_messageid_description"),
    )
    async def removescheduled(self, interaction: discord.Interaction, messageid: int) -> None:
        await interaction.response.defer()
        from typing import cast

        command_info = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,  # type: ignore[arg-type]
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await removeScheduledCommand(command_info=command_info, message_id=messageid)


class UtilityCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name=app_commands.locale_str("utility_help_name"),
        description=app_commands.locale_str("utility_help_description"),
    )
    async def help_slash(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast

        command_info = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,  # type: ignore[arg-type]
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await helpCommand(command_info=command_info)
        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        utility_cmds = UtilityCommands(
            name=app_commands.locale_str("utilitycmd_name"),
            description=app_commands.locale_str("utilitycmd_description"),
        )
        message_tracking_cmds = MessageTrackingCommands(
            name=app_commands.locale_str("utility_messagetracking_name"),
            description=app_commands.locale_str("utility_messagetracking_description"),
        )
        utility_cmds.add_command(message_tracking_cmds)
        auto_publish_cmds = AutoPublishCommands(
            name=app_commands.locale_str("utility_autopublish_name"),
            description=app_commands.locale_str("utility_autopublish_description"),
        )
        utility_cmds.add_command(auto_publish_cmds)
        booster_role_cmds = BoosterRoleCommands(
            name=app_commands.locale_str("utility_boosterrole_name"),
            description=app_commands.locale_str("utility_boosterrole_description"),
        )
        utility_cmds.add_command(booster_role_cmds)
        booster_channel_cmds = BoosterChannelCommands(
            name=app_commands.locale_str("utility_boosterchannel_name"),
            description=app_commands.locale_str("utility_boosterchannel_description"),
        )
        utility_cmds.add_command(booster_channel_cmds)
        scheduled_message_cmds = ScheduledMessageCommands(
            name=app_commands.locale_str("utility_scheduledmessage_name"),
            description=app_commands.locale_str("utility_scheduledmessage_description"),
        )
        utility_cmds.add_command(scheduled_message_cmds)
        brawl_stars_cmds = BrawlStarsCommands(
            name=app_commands.locale_str("utility_bs_name"),
            description=app_commands.locale_str("utility_bs_description"),
        )
        utility_cmds.add_command(brawl_stars_cmds)
        twitch_cmds = TwitchCommands(
            name=app_commands.locale_str("utility_twitch_name"),
            description=app_commands.locale_str("utility_twitch_description"),
        )
        utility_cmds.add_command(twitch_cmds)
        self.bot.tree.add_command(utility_cmds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilityCog(bot))
