from locale_keys import locale
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.utility.afk import afk as afkCommand
from commands.utility.autopublish import autopublish as autopublishCommand
from commands.utility.autopublish import autopublish_remove as autopublishRemoveCommand
from commands.utility.avatar import avatar as avatarCommand
from commands.utility.avatar_decoration import avatarDecoration as avatarDecorationCommand
from commands.utility.banner import banner as bannerCommand
from commands.utility.brawlstars.battlelog import battlelog as battlelogCommand
from commands.utility.brawlstars.brawlers import brawlers as brawlstarsBrawlersCommand
from commands.utility.brawlstars.club import club as brawlstarsClubCommand
from commands.utility.brawlstars.events import events as brawlstarsEventsCommand
from commands.utility.brawlstars.link import link as brawlstarsLinkCommand
from commands.utility.brawlstars.playerinfo import player_info as brawlstarsPlayerInfoCommand
from commands.utility.brawlstars.unlink import unlink as brawlstarsUnlinkCommand
from commands.utility.claim_booster_channel import claimBoosterChannel as claimboosterchannelCommand
from commands.utility.claim_booster_role import claimBoosterRole as claimboosterroleCommand
from commands.utility.delete_booster_channel import deleteBoosterChannel as deleteboosterchannelCommand
from commands.utility.delete_booster_role import deleteBoosterRole as deleteboosterroleCommand
from commands.utility.feedback import feedback as feedbackCommand
from commands.utility.help import help as helpCommand
from commands.utility.listscheduled import list_scheduled_messages as listScheduledCommand
from commands.utility.messagetrackingoptin import optIn as optInCommand
from commands.utility.messagetrackingoptout import optOut as optOutCommand
from commands.utility.removescheduled import remove_scheduled_message as removeScheduledCommand
from commands.utility.report import report as reportCommand
from commands.utility.schedulemessage import schedule_message as scheduleMessageCommand
from commands.utility.setup_booster_channel import setupBoosterChannel as setupboosterchannelCommand
from commands.utility.setup_booster_role import setupBoosterRole as setupboosterroleCommand
from commands.utility.twitch.add_twitch_live_notification import addTwitchLiveNotification as addTwitchLiveNotificationCommand
from commands.utility.twitch.see_twitch_live_notifications import seeTwitchLiveNotifications as seeTwitchLiveNotificationsCommand
from utility import EmbedColor

class MessageTrackingCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.messageoptout.name.discord_key, description=locale.utility.messageoptout.description.discord_key)
    async def messagetrackingoptout(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await optOutCommand(command_info=command_info)

    @app_commands.command(name=locale.utility.messageoptin.name.discord_key, description=locale.utility.messageoptin.description.discord_key)
    async def messagetrackingoptin(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await optInCommand(command_info=command_info)

class BoosterRoleCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.claimboosterrole.name.discord_key, description=locale.utility.claimboosterrole.description.discord_key)
    @app_commands.describe(name=locale.utility.claimboosterrole.params.name.description.discord_key, color=locale.utility.claimboosterrole.params.color.description.discord_key, icon=locale.utility.claimboosterrole.params.icon.description.discord_key)
    async def claimboosterrole(self, ctx, name: app_commands.Range[str, 1, 100], color: app_commands.Range[str, 6, 7]=None, icon: discord.Attachment=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await claimboosterroleCommand(command_info=command_info, name=name, color=color, icon=icon)

    @app_commands.command(name=locale.utility.deleteboosterrole.name.discord_key, description=locale.utility.deleteboosterrole.description.discord_key)
    async def deleteboosterrole(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await deleteboosterroleCommand(command_info=command_info)

    @app_commands.command(name=locale.utility.setupboosterrole.name.discord_key, description=locale.utility.setupboosterrole.description.discord_key)
    @app_commands.describe(role=locale.utility.setupboosterrole.params.role.description.discord_key)
    async def setupboosterrole(self, ctx, role: discord.Role) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await setupboosterroleCommand(command_info=command_info, role=role)

    @app_commands.command(name=locale.utility.boosterroleinfo.name.discord_key, description=locale.utility.boosterroleinfo.description.discord_key)
    async def info(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        embed = utility.tanjunEmbed(colour=EmbedColor.INFO, title=locale.commands.utility.boosterroleinfo.info.title(str(command_info.locale)), description=locale.commands.utility.boosterroleinfo.info.description(str(command_info.locale)))
        await command_info.reply(embed=embed)

class BoosterChannelCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.claimboosterchannel.name.discord_key, description=locale.utility.claimboosterchannel.description.discord_key)
    @app_commands.describe(name=locale.utility.claimboosterchannel.params.name.description.discord_key)
    async def claimboosterchannel(self, ctx, name: app_commands.Range[str, 1, 100]) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await claimboosterchannelCommand(command_info=command_info, name=name)

    @app_commands.command(name=locale.utility.deleteboosterch.name.discord_key, description=locale.utility.deleteboosterchannel.description.discord_key)
    async def deleteboosterchannel(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await deleteboosterchannelCommand(command_info=command_info)

    @app_commands.command(name=locale.utility.setupboosterchannel.name.discord_key, description=locale.utility.setupboosterchannel.description.discord_key)
    @app_commands.describe(category=locale.utility.setupboosterchannel.params.category.description.discord_key)
    async def setupboosterchannel(self, ctx, category: discord.CategoryChannel) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await setupboosterchannelCommand(command_info=command_info, category=category)

    @app_commands.command(name=locale.utility.boosterchannelinfo.name.discord_key, description=locale.utility.boosterchannelinfo.description.discord_key)
    async def info(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        embed = utility.tanjunEmbed(colour=EmbedColor.INFO, title=locale.commands.utility.boosterchannelinfo.info.title(str(command_info.locale)), description=locale.commands.utility.boosterchannelinfo.info.description(command_info.locale))
        await command_info.reply(embed=embed)

class AutoPublishCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.autopublish.name.discord_key, description=locale.utility.autopublish.description.discord_key)
    @app_commands.describe(channel=locale.utility.autopublish.params.channel.description.discord_key)
    async def autopublish(self, ctx, channel: discord.TextChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not channel:
            channel = ctx.channel
        await autopublishCommand(command_info=command_info, channel=channel)

    @app_commands.command(name=locale.utility.autopublish.remove.name.discord_key, description=locale.utility.autopublish.remove.description.discord_key)
    @app_commands.describe(channel=locale.utility.autopublish.remove.params.channel.description.discord_key)
    async def autopublish_remove(self, ctx, channel: discord.TextChannel=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not channel:
            channel = ctx.channel
        await autopublishRemoveCommand(command_info=command_info, channel=channel)

class BrawlStarsCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.bs.battlelog.name.discord_key, description=locale.utility.bs.battlelog.description.discord_key)
    @app_commands.describe(tag=locale.utility.bs.battlelog.params.tag.description.discord_key)
    async def battlelog(self, ctx, tag: str | None=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await battlelogCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(name=locale.utility.bs.playerinfo.name.discord_key, description=locale.utility.bs.playerinfo.description.discord_key)
    @app_commands.describe(tag=locale.utility.bs.playerinfo.params.tag.description.discord_key)
    async def playerinfo(self, ctx, tag: str | None=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsPlayerInfoCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(name=locale.utility.bs.brawlers.name.discord_key, description=locale.utility.bs.brawlers.description.discord_key)
    @app_commands.describe(tag=locale.utility.bs.brawlers.params.tag.description.discord_key)
    async def brawlers(self, ctx, tag: str | None=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsBrawlersCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(name=locale.utility.bs.club.name.discord_key, description=locale.utility.bs.club.description.discord_key)
    @app_commands.describe(tag=locale.utility.bs.club.params.tag.description.discord_key)
    async def club(self, ctx, tag: str) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsClubCommand(command_info=command_info, club_tag=tag)
        return

    @app_commands.command(name=locale.utility.bs.events.name.discord_key, description=locale.utility.bs.events.description.discord_key)
    async def events(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsEventsCommand(command_info=command_info)
        return

    @app_commands.command(name=locale.utility.bs.link.name.discord_key, description=locale.utility.bs.link.description.discord_key)
    @app_commands.describe(tag=locale.utility.bs.link.params.tag.description.discord_key)
    async def link(self, ctx, tag: str) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsLinkCommand(command_info=command_info, player_tag=tag)
        return

    @app_commands.command(name=locale.utility.bs.unlink.name.discord_key, description=locale.utility.bs.unlink.description.discord_key)
    async def unlink(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await brawlstarsUnlinkCommand(command_info=command_info)
        return

class TwitchCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.twitch.add.name.discord_key, description=locale.utility.twitch.add.description.discord_key)
    @app_commands.describe(twitchname=locale.utility.twitch.add.params.twitchname.description.discord_key, channel=locale.utility.twitch.add.params.channel.description.discord_key, notificationmessage=locale.utility.twitch.add.params.notificationmessage.description.discord_key)
    async def add(self, ctx, twitchname: str, channel: discord.TextChannel, notificationmessage: app_commands.Range[str, 0, 1024]=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await addTwitchLiveNotificationCommand(command_info=command_info, twitch_name=twitchname, channel=channel, notification_message=notificationmessage)
        return

    @app_commands.command(name=locale.utility.twitch.see.name.discord_key, description=locale.utility.twitch.see.description.discord_key)
    async def see(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await seeTwitchLiveNotificationsCommand(command_info=command_info)
        return

class UtilityCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.avatar.name.discord_key, description=locale.utility.avatar.description.discord_key)
    @app_commands.describe(user=locale.utility.avatar.params.user.description.discord_key)
    async def avatar(self, ctx, user: discord.Member=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not user:
            user = ctx.user
        await avatarCommand(command_info=command_info, user=user)

    @app_commands.command(name=locale.utility.banner.name.discord_key, description=locale.utility.banner.description.discord_key)
    @app_commands.describe(user=locale.utility.banner.params.user.description.discord_key)
    async def banner(self, ctx, user: discord.Member=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not user:
            user = ctx.user
        await bannerCommand(command_info=command_info, user=user)

    @app_commands.command(name=locale.utility.avatardecoration.name.discord_key, description=locale.utility.avatardecoration.description.discord_key)
    @app_commands.describe(user=locale.utility.avatardecoration.params.user.description.discord_key)
    async def avatardecoration(self, ctx, user: discord.Member=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        if not user:
            user = ctx.user
        await avatarDecorationCommand(command_info=command_info, user=user)

    @app_commands.command(name=locale.utility.feedback.name.discord_key, description=locale.utility.feedback.description.discord_key)
    async def feedback(self, ctx) -> None:
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.response.send_message, client=ctx.client)
        await feedbackCommand(command_info=command_info, ctx=ctx)

    @app_commands.command(name=locale.utility.afk.name.discord_key, description=locale.utility.afk.description.discord_key)
    @app_commands.describe(reason=locale.utility.afk.params.reason.description.discord_key)
    async def afk(self, ctx, reason: app_commands.Range[str, 0, 1000]) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await afkCommand(command_info=command_info, reason=reason)

    @app_commands.command(name=locale.utility.report.name.discord_key, description=locale.utility.report.description.discord_key)
    @app_commands.describe(user=locale.utility.report.params.user.description.discord_key, reason=locale.utility.report.params.reason.description.discord_key, attachment=locale.utility.report.params.attachment.description.discord_key, anonymous=locale.utility.report.params.anonymous.description.discord_key)
    async def report(self, ctx, user: discord.Member, reason: app_commands.Range[str, 12, 1024], attachment: discord.Attachment | None=None, anonymous: bool=False) -> None:
        await ctx.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await reportCommand(command_info=command_info, user=user, reason=reason, attachment=attachment, anonymous=anonymous)

class ScheduledMessageCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.utility.schedulemessage.name.discord_key, description=locale.utility.schedulemessage.description.discord_key)
    @app_commands.describe(content=locale.utility.schedulemessage.params.content.description.discord_key, sendin=locale.utility.schedulemessage.params.sendin.description.discord_key, channel=locale.utility.schedulemessage.params.channel.description.discord_key, repeatinterval=locale.utility.schedulemessage.params.repeat.description.discord_key, repeatamount=locale.utility.schedulemessage.params.repeatamount.description.discord_key, attachment1=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment2=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment3=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment4=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment5=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment6=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment7=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment8=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment9=locale.utility.schedulemessage.params.attachment.description.discord_key, attachment10=locale.utility.schedulemessage.params.attachment.description.discord_key)
    async def schedulemessage(self, ctx, content: app_commands.Range[str, 1, 1024], sendin: app_commands.Range[str, 1, 100], channel: discord.TextChannel=None, repeatinterval: app_commands.Range[str, 0, 15]=None, repeatamount: app_commands.Range[int, 0, 1000]=None, attachment1: discord.Attachment=None, attachment2: discord.Attachment=None, attachment3: discord.Attachment=None, attachment4: discord.Attachment=None, attachment5: discord.Attachment=None, attachment6: discord.Attachment=None, attachment7: discord.Attachment=None, attachment8: discord.Attachment=None, attachment9: discord.Attachment=None, attachment10: discord.Attachment=None) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        attachments: list[discord.Attachment] = [a for a in [attachment1, attachment2, attachment3, attachment4, attachment5, attachment6, attachment7, attachment8, attachment9, attachment10] if a is not None]
        await scheduleMessageCommand(command_info=command_info, content=content, send_in=sendin, channel=channel, repeat=repeatinterval, repeat_amount=repeatamount, attachments=attachments or [])

    @app_commands.command(name=locale.utility.listscheduled.name.discord_key, description=locale.utility.listscheduled.description.discord_key)
    async def listscheduled(self, ctx) -> None:
        await ctx.response.defer()
        command_info = utility.CommandInfo(user=ctx.user, channel=ctx.channel, guild=ctx.guild, command=ctx.command, locale=ctx.locale, message=ctx.message, permissions=ctx.permissions, reply=ctx.followup.send, client=ctx.client)
        await listScheduledCommand(command_info=command_info)

    @app_commands.command(name=locale.utility.removescheduled.name.discord_key, description=locale.utility.removescheduled.description.discord_key)
    @app_commands.describe(messageid=locale.utility.removescheduled.params.messageid.description.discord_key)
    async def removescheduled(self, interaction: discord.Interaction, messageid: int) -> None:
        await interaction.response.defer()
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeScheduledCommand(command_info=command_info, message_id=messageid)

class UtilityCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name=locale.utility.help.name.discord_key, description=locale.utility.help.description.discord_key)
    async def help_slash(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        from typing import cast
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await helpCommand(command_info=command_info, ctx=interaction)
        return

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        utility_cmds = UtilityCommands(name=locale.utilitycmd.name.discord_key, description=locale.utilitycmd.description.discord_key)
        message_tracking_cmds = MessageTrackingCommands(name=locale.utility.messagetracking.name.discord_key, description=locale.utility.messagetracking.description.discord_key)
        utility_cmds.add_command(message_tracking_cmds)
        auto_publish_cmds = AutoPublishCommands(name=locale.utility.autopublish.name.discord_key, description=locale.utility.autopublish.description.discord_key)
        utility_cmds.add_command(auto_publish_cmds)
        booster_role_cmds = BoosterRoleCommands(name=locale.utility.boosterrole.name.discord_key, description=locale.utility.boosterrole.description.discord_key)
        utility_cmds.add_command(booster_role_cmds)
        booster_channel_cmds = BoosterChannelCommands(name=locale.utility.boosterchannel.name.discord_key, description=locale.utility.boosterchannel.description.discord_key)
        utility_cmds.add_command(booster_channel_cmds)
        scheduled_message_cmds = ScheduledMessageCommands(name=locale.utility.scheduledmessage.name.discord_key, description=locale.utility.scheduledmessage.description.discord_key)
        self.bot.tree.add_command(scheduled_message_cmds)
        brawl_stars_cmds = BrawlStarsCommands(name=locale.utility.bs.name.discord_key, description=locale.utility.bs.description.discord_key)
        utility_cmds.add_command(brawl_stars_cmds)
        twitch_cmds = TwitchCommands(name=locale.utility.twitch.name.discord_key, description=locale.utility.twitch.description.discord_key)
        utility_cmds.add_command(twitch_cmds)
        self.bot.tree.add_command(utility_cmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilityCog(bot))