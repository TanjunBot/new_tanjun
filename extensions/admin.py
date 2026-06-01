from __future__ import annotations
from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.admin.addrole import addrole as addroleCommand
from commands.admin.ban import ban as banCommand
from commands.admin.boosterrole import create_booster_role as CreateBoosterRoleCommand
from commands.admin.copy_7tv_emote import copy_7tv_emote as copy7tvEmoteCommand
from commands.admin.copy_emoji import copy_emoji as copyEmojiCommand
from commands.admin.copyrole import copyrole as copyRoleCommand
from commands.admin.createemoji import create_emoji as createEmojiCommand
from commands.admin.createrole import createrole as createroleCommand
from commands.admin.deleterole import deleterole as deleteroleCommand
from commands.admin.embedcreator import create_embed as createEmbedCommand
from commands.admin.join_to_create.jointocreatechannel import jointocreatechannel as jointoCreateChannelCommand
from commands.admin.join_to_create.removejointocreatechannel import removejointocreatechannel as removeJoinToCreateChannelCommand
from commands.admin.kick import kick as kickCommand
from commands.admin.lock import lock_channel as lockChannelCommand
from commands.admin.moverole import moverole as moveroleCommand
from commands.admin.nickname import change_nickname as changeNicknameCommand
from commands.admin.nuke import nuke_channel as nukeChannelCommand
from commands.admin.purge import purge as purgeCommand
from commands.admin.removerole import removerole as removeroleCommand
from commands.admin.removetimeout import remove_timeout as removeTimeoutCommand
from commands.admin.reports.remove_channel import remove_channel as removeReportChannelCommand
from commands.admin.reports.set_channel import set_channel as setReportChannelCommand
from commands.admin.reports.show_reports import show_reports as showReportsCommand
from commands.admin.reports.unblock_reporter import unblock_reporter_cmd as unblockReporterCommand
from commands.admin.say import say as sayCommand
from commands.admin.set_locale import set_locale as setLocaleCommand
from commands.admin.slowmode import set_slowmode as setSlowmodeCommand
from commands.admin.ticket.create_ticket import create_ticket as createTicketCommand
from commands.admin.timeout import timeout as timeoutCommand
from commands.admin.trigger_messages.add import add_trigger_message as addTriggerMessageCommand
from commands.admin.trigger_messages.configure import configure_trigger_messages as configureTriggerMessagesCommand
from commands.admin.unban import unban as unbanCommand
from commands.admin.unlock import unlock_channel as unlockChannelCommand
from commands.admin.viewwarns import view_warnings as viewWarningsCommand
from commands.admin.warn import warn_user as warnUserCommand
from commands.admin.warnconfig import warn_config as warnConfigCommand

class WarnCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.warn.add.name.discord_key, description=locale.admin.warn.add.description.discord_key)
    @app_commands.describe(user=locale.admin.warn.add.params.member.description.discord_key, reason=locale.admin.warn.add.params.reason.description.discord_key)
    async def add(self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await warnUserCommand(command_info=command_info, member=user, reason=reason)
        return

    @app_commands.command(name=locale.admin.warn.view.name.discord_key, description=locale.admin.warn.view.description.discord_key)
    @app_commands.describe(user=locale.admin.warn.view.params.member.description.discord_key)
    async def view(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await viewWarningsCommand(command_info=command_info, member=user)
        return

    @app_commands.command(name=locale.admin.warn.config.name.discord_key, description=locale.admin.warn.config.description.discord_key)
    async def config(self, interaction: discord.Interaction) -> None:
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.response.send_modal, client=interaction.client)
        await warnConfigCommand(command_info=command_info)
        return

class RoleCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.addrole.name.discord_key, description=locale.admin.addrole.description.discord_key)
    @app_commands.describe(user=locale.admin.addrole.params.user.name.discord_key, role=locale.admin.addrole.params.role.name.discord_key)
    async def addrole(self, interaction: discord.Interaction, user: discord.Member=None, role: discord.Role=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await addroleCommand(command_info=command_info, user=user, role=role)
        return

    @app_commands.command(name=locale.admin.removerole.name.discord_key, description=locale.admin.removerole.description.discord_key)
    @app_commands.describe(user=locale.admin.removerole.params.user.description.discord_key, role=locale.admin.removerole.params.role.description.discord_key)
    async def removerole(self, interaction: discord.Interaction, user: discord.Member=None, role: discord.Role=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeroleCommand(command_info=command_info, user=user, role=role)
        return

class RoleManageCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.createrole.name.discord_key, description=locale.admin.createrole.description.discord_key)
    @app_commands.describe(name=locale.admin.createrole.params.name.description.discord_key, color=locale.admin.createrole.params.color.description.discord_key, display_icon=locale.admin.createrole.params.displayicon.description.discord_key, hoist=locale.admin.createrole.params.hoist.description.discord_key, mentionable=locale.admin.createrole.params.mentionable.description.discord_key, reason=locale.admin.createrole.params.reason.description.discord_key, display_emoji=locale.admin.createrole.params.displayemoji.description.discord_key)
    async def createrole(self, interaction: discord.Interaction, name: app_commands.Range[str, 1, 100], color: app_commands.Range[str, 6, 7]=None, display_icon: discord.Attachment=None, hoist: bool=False, mentionable: bool=False, reason: app_commands.Range[str, 0, 100]=None, display_emoji: app_commands.Range[str, 0, 1]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await createroleCommand(command_info=command_info, name=name, color=color, display_icon=display_icon if display_icon else display_emoji, hoist=hoist, mentionable=mentionable, reason=reason)
        return

    @app_commands.command(name=locale.admin.deleterole.name.discord_key, description=locale.admin.deleterole.description.discord_key)
    @app_commands.describe(role=locale.admin.deleterole.params.role.description.discord_key, reason=locale.admin.deleterole.params.reason.description.discord_key)
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role, reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await deleteroleCommand(command_info=command_info, role=role, reason=reason)
        return

    @app_commands.command(name=locale.admin.moverole.name.discord_key, description=locale.admin.moverole.description.discord_key)
    @app_commands.describe(role=locale.admin.moverole.params.role.description.discord_key, target_role=locale.admin.moverole.params.targetrole.description.discord_key, position=locale.admin.moverole.params.position.description.discord_key)
    @app_commands.choices(position=[app_commands.Choice(name=locale.admin.moverole.params.position.above.discord_key, value='above'), app_commands.Choice(name=locale.admin.moverole.params.position.below.discord_key, value='below')])
    async def moverole(self, interaction: discord.Interaction, role: discord.Role, target_role: discord.Role, position: app_commands.Choice[str]) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await moveroleCommand(command_info=command_info, role=role, target_role=target_role, position=position.value)

    @app_commands.command(name=locale.admin.copyrole.name.discord_key, description=locale.admin.copyrole.description.discord_key)
    @app_commands.describe(role=locale.admin.copyrole.params.role.description.discord_key, copymembers=locale.admin.copyrole.params.copymembers.description.discord_key)
    @app_commands.choices(copymembers=[app_commands.Choice(name=locale.admin.copyrole.params.copymembers.true.discord_key, value='true'), app_commands.Choice(name=locale.admin.copyrole.params.copymembers.false.discord_key, value='false')])
    async def copyrole(self, interaction: discord.Interaction, role: discord.Role, copymembers: app_commands.Choice[str]) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await copyRoleCommand(command_info=command_info, role=role, copy_members=copymembers.value == 'true')
        return

class ReportCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.rps.setchannel.name.discord_key, description=locale.admin.rps.setchannel.description.discord_key)
    @app_commands.describe(channel=locale.admin.rps.setchannel.params.channel.description.discord_key)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = interaction.channel
        await setReportChannelCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.admin.rps.removechannel.name.discord_key, description=locale.admin.rps.removechannel.description.discord_key)
    async def remove_channel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeReportChannelCommand(command_info=command_info)
        return

    @app_commands.command(name=locale.admin.rps.showreports.name.discord_key, description=locale.admin.rps.showreports.description.discord_key)
    @app_commands.describe(user=locale.admin.rps.showreports.params.user.description.discord_key)
    async def show_reports(self, interaction: discord.Interaction, user: discord.Member=None) -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await showReportsCommand(command_info=command_info, user=user)
        return

    @app_commands.command(name=locale.admin.rps.unblockreporter.name.discord_key, description=locale.admin.rps.unblockreporter.description.discord_key)
    @app_commands.describe(user=locale.admin.rps.unblockreporter.params.user.description.discord_key)
    async def unblock_reporter(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await unblockReporterCommand(command_info=command_info, user=user)
        return

class TriggerMessagesCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.tm.configure.name.discord_key, description=locale.admin.tm.configure.description.discord_key)
    async def configure(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await configureTriggerMessagesCommand(command_info=command_info)
        return

    @app_commands.command(name=locale.admin.tm.add.name.discord_key, description=locale.admin.tm.add.description.discord_key)
    @app_commands.describe(trigger=locale.admin.tm.add.params.trigger.description.discord_key, response=locale.admin.tm.add.params.response.description.discord_key, casesensitive=locale.admin.tm.add.params.casesensitive.description.discord_key)
    @app_commands.choices(casesensitive=[app_commands.Choice(name=locale.admin.tm.add.params.casesensitive.true.discord_key, value='t'), app_commands.Choice(name=locale.admin.tm.add.params.casesensitive.false.discord_key, value='f')])
    async def add(self, interaction: discord.Interaction, trigger: app_commands.Range[str, 1, 128], response: app_commands.Range[str, 1, 1024], casesensitive: app_commands.Choice[str]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await addTriggerMessageCommand(command_info=command_info, trigger=trigger, response=response, case_sensitive=casesensitive.value == 't' if casesensitive else False)
        return

class JoinToCreateCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.jtc.setchannel.name.discord_key, description=locale.admin.jtc.setchannel.description.discord_key)
    @app_commands.describe(channel=locale.admin.jtc.setchannel.params.channel.description.discord_key)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await jointoCreateChannelCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.admin.jtc.removechannel.name.discord_key, description=locale.admin.jtc.removechannel.description.discord_key)
    @app_commands.describe(channel=locale.admin.jtc.removechannel.params.channel.description.discord_key)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeJoinToCreateChannelCommand(command_info=command_info, channel=channel)
        return

class AdminModerationCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.kick.name.discord_key, description=locale.admin.kick.description.discord_key)
    @app_commands.describe(user=locale.admin.kick.params.user.description.discord_key, reason=locale.admin.kick.params.reason.description.discord_key)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await kickCommand(command_info=command_info, target=user, reason=reason)
        return

    @app_commands.command(name=locale.admin.ban.name.discord_key, description=locale.admin.ban.description.discord_key)
    @app_commands.describe(user=locale.admin.ban.params.user.description.discord_key, reason=locale.admin.ban.params.reason.description.discord_key, delete_message_days=locale.admin.ban.params.deletemessagedays.description.discord_key)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 0, 100]=None, delete_message_days: app_commands.Range[int, 0, 7]=0) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await banCommand(command_info=command_info, target=user, reason=reason, delete_message_days=delete_message_days)
        return

    @app_commands.command(name=locale.admin.unban.name.discord_key, description=locale.admin.unban.description.discord_key)
    @app_commands.describe(username=locale.admin.unban.params.username.description.discord_key, reason=locale.admin.unban.params.reason.description.discord_key)
    async def unban(self, interaction: discord.Interaction, username: app_commands.Range[str, 1, 100], reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await unbanCommand(command_info=command_info, username=username, reason=reason)
        return

    @app_commands.command(name=locale.admin.timeout.name.discord_key, description=locale.admin.timeout.description.discord_key)
    @app_commands.describe(user=locale.admin.timeout.params.member.description.discord_key, duration=locale.admin.timeout.params.duration.description.discord_key, reason=locale.admin.timeout.params.reason.description.discord_key)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: app_commands.Range[int, 1, 40320], reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await timeoutCommand(command_info=command_info, member=user, duration=duration, reason=reason)
        return

    @app_commands.command(name=locale.admin.removetimeout.name.discord_key, description=locale.admin.removetimeout.description.discord_key)
    @app_commands.describe(user=locale.admin.removetimeout.params.member.description.discord_key, reason=locale.admin.removetimeout.params.reason.description.discord_key)
    async def removetimeout(self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeTimeoutCommand(command_info=command_info, member=user, reason=reason)
        return

    @app_commands.command(name=locale.admin.nickname.name.discord_key, description=locale.admin.nickname.description.discord_key)
    @app_commands.describe(user=locale.admin.nickname.params.member.description.discord_key, nickname=locale.admin.nickname.params.nickname.description.discord_key)
    async def nickname(self, interaction: discord.Interaction, user: discord.Member, nickname: app_commands.Range[str, 0, 100]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await changeNicknameCommand(command_info=command_info, member=user, nickname=nickname)
        return

class AdminPurgeCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.purge.name.discord_key, description=locale.admin.purge.description.discord_key)
    @app_commands.describe(limit=locale.admin.purge.params.amount.description.discord_key, channel=locale.admin.purge.params.channel.description.discord_key, setting=locale.admin.purge.params.setting.description.discord_key)
    @app_commands.choices(setting=[app_commands.Choice(value='all', name=locale.admin.purge.params.setting.all.discord_key), app_commands.Choice(value='bot', name=locale.admin.purge.params.setting.bot.discord_key), app_commands.Choice(value='user', name=locale.admin.purge.params.setting.user.discord_key), app_commands.Choice(value='notPinned', name=locale.admin.purge.params.setting.notPinned.discord_key), app_commands.Choice(value='userNotPinned', name=locale.admin.purge.params.setting.userNotPinned.discord_key), app_commands.Choice(value='botNotPinned', name=locale.admin.purge.params.setting.botNotPinned.discord_key), app_commands.Choice(value='notadmin', name=locale.admin.purge.params.setting.notAdmin.discord_key), app_commands.Choice(value='notUserAdmin', name=locale.admin.purge.params.setting.notUserAdmin.discord_key), app_commands.Choice(value='embeds', name=locale.admin.purge.params.setting.embeds.discord_key), app_commands.Choice(value='files', name=locale.admin.purge.params.setting.files.discord_key), app_commands.Choice(value='notAdminNotPinned', name=locale.admin.purge.params.setting.notAdminNotPinned.discord_key)])
    async def purge(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 1000], channel: discord.TextChannel=None, setting: app_commands.Choice[str]='all') -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await purgeCommand(command_info=command_info, amount=limit, channel=channel, setting=setting.value if setting != 'all' else 'all')
        return

class AdminChannelCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.slowmode.name.discord_key, description=locale.admin.slowmode.description.discord_key)
    @app_commands.describe(seconds=locale.admin.slowmode.params.seconds.description.discord_key, channel=locale.admin.slowmode.params.channel.description.discord_key)
    async def slowmode(self, interaction: discord.Interaction, seconds: app_commands.Range[int, 1, 21600], channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await setSlowmodeCommand(command_info=command_info, seconds=seconds, channel=channel)
        return

    @app_commands.command(name=locale.admin.lock.name.discord_key, description=locale.admin.lock.description.discord_key)
    @app_commands.describe(channel=locale.admin.lock.params.channel.description.discord_key)
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await lockChannelCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.admin.unlock.name.discord_key, description=locale.admin.unlock.description.discord_key)
    @app_commands.describe(channel=locale.admin.unlock.params.channel.description.discord_key)
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await unlockChannelCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.admin.nuke.name.discord_key, description=locale.admin.nuke.description.discord_key)
    @app_commands.describe(channel=locale.admin.nuke.params.channel.description.discord_key)
    async def nuke(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = interaction.channel
        await nukeChannelCommand(command_info=command_info, channel=channel)
        return

class AdminMessagingCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.say.name.discord_key, description=locale.admin.say.description.discord_key)
    @app_commands.describe(channel=locale.admin.say.params.channel.description.discord_key, message=locale.admin.say.params.message.description.discord_key)
    async def say(self, interaction: discord.Interaction, message: app_commands.Range[str, 1, 2000], channel: discord.TextChannel=None) -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = interaction.channel
        await sayCommand(command_info=command_info, channel=channel, message=message)
        return

    @app_commands.command(name=locale.admin.embed.name.discord_key, description=locale.admin.embed.description.discord_key)
    @app_commands.describe(title=locale.admin.embed.params.title.description.discord_key, channel=locale.admin.embed.params.channel.description.discord_key)
    async def embed(self, interaction: discord.Interaction, title: app_commands.Range[str, 1, 256], channel: discord.TextChannel=None) -> None:
        await interaction.response.defer(ephemeral=True)
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if channel is None:
            channel = interaction.channel
        await createEmbedCommand(command_info=command_info, channel=channel, title=title)
        return

class AdminEmojiCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.createemoji.name.discord_key, description=locale.admin.createemoji.description.discord_key)
    @app_commands.describe(name=locale.admin.createemoji.params.name.description.discord_key, imageurl=locale.admin.createemoji.params.imageUrl.description.discord_key)
    async def createemoji(self, interaction: discord.Interaction, name: str, imageurl: str) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        view = discord.ui.View()
        role_select = discord.ui.RoleSelect(placeholder=locale.commands.admin.createEmoji.role_selectPlaceholder(interaction.locale), default_values=[interaction.guild.default_role], min_values=1, max_values=25)

        async def role_select_callback(select_interaction: discord.Interaction) -> None:
            roles = [interaction.guild.get_role(int(r)) for r in select_interaction.data['values']]
            command_info.message = select_interaction.message
            command_info.reply = select_interaction.response.send_message
            await createEmojiCommand(command_info=command_info, name=name, image_url=imageurl, roles=roles)
        role_select.callback = role_select_callback
        view.add_item(role_select)
        await interaction.followup.send(locale.commands.admin.createEmoji.role_select(interaction.locale), view=view)

    @app_commands.command(name=locale.admin.copyemoji.name.discord_key, description=locale.admin.copyemoji.description.discord_key)
    @app_commands.describe(emoji=locale.admin.copyemoji.params.emoji.description.discord_key)
    async def copy_emoji(self, interaction: discord.Interaction, emoji: str) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await copyEmojiCommand(command_info=command_info, emoji=emoji)
        return

    @app_commands.command(name=locale.admin.copy7tv.name.discord_key, description=locale.admin.copy7tv.description.discord_key)
    @app_commands.describe(twitch_username=locale.admin.copy7tv.params.twitch.username.description.discord_key)
    async def copy_7tv(self, interaction: discord.Interaction, twitch_username: str) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await copy7tvEmoteCommand(command_info=command_info, twitch_username=twitch_username)
        return

    @app_commands.command(name=locale.admin.boosterrole.name.discord_key, description=locale.admin.boosterrole.description.discord_key)
    @app_commands.describe(role=locale.admin.boosterrole.params.role.description.discord_key)
    async def claimboosterrole(self, interaction: discord.Interaction, role: discord.Role=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await CreateBoosterRoleCommand(command_info=command_info, role=role)

class AdminSetupCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.createticket.name.discord_key, description=locale.admin.createticket.description.discord_key)
    @app_commands.describe(name=locale.admin.createticket.params.name.description.discord_key, description=locale.admin.createticket.params.description.description.discord_key, channel=locale.admin.createticket.params.channel.description.discord_key, pingrole=locale.admin.createticket.params.pingrole.description.discord_key, summarychannel=locale.admin.createticket.params.summarychannel.description.discord_key, introduction=locale.admin.createticket.params.introduction.description.discord_key)
    async def create_ticket(self, interaction: discord.Interaction, name: app_commands.Range[str, 1, 128], description: app_commands.Range[str, 1, 1024], channel: discord.TextChannel=None, pingrole: discord.Role=None, summarychannel: discord.TextChannel=None, introduction: app_commands.Range[str, 0, 1024]=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = interaction.channel
        await createTicketCommand(command_info=command_info, channel=channel, name=name, description=description, ping_role=pingrole, summary_channel=summarychannel, introduction=introduction)
        return

class AdminLocaleCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.admin.setlocale.name.discord_key, description=locale.admin.setlocale.description.discord_key)
    @app_commands.describe(locale=locale.admin.setlocale.params.locale.description.discord_key)
    @app_commands.choices(locale=[app_commands.Choice(value='bg', name=locale.games.hangman.params.language.bg.discord_key), app_commands.Choice(value='cs', name=locale.games.hangman.params.language.cs.discord_key), app_commands.Choice(value='da', name=locale.games.hangman.params.language.da.discord_key), app_commands.Choice(value='de', name=locale.games.hangman.params.language.de.discord_key), app_commands.Choice(value='el', name=locale.games.hangman.params.language.el.discord_key), app_commands.Choice(value='en', name=locale.games.hangman.params.language.en.discord_key), app_commands.Choice(value='es', name=locale.games.hangman.params.language.es.discord_key), app_commands.Choice(value='fi', name=locale.games.hangman.params.language.fi.discord_key), app_commands.Choice(value='fr', name=locale.games.hangman.params.language.fr.discord_key), app_commands.Choice(value='hi', name=locale.games.hangman.params.language.hi.discord_key), app_commands.Choice(value='hu', name=locale.games.hangman.params.language.hu.discord_key), app_commands.Choice(value='id', name=locale.games.hangman.params.language.id.discord_key), app_commands.Choice(value='it', name=locale.games.hangman.params.language.it.discord_key), app_commands.Choice(value='ja', name=locale.games.hangman.params.language.ja.discord_key), app_commands.Choice(value='ko', name=locale.games.hangman.params.language.ko.discord_key), app_commands.Choice(value='lt', name=locale.games.hangman.params.language.lt.discord_key), app_commands.Choice(value='nb', name=locale.games.hangman.params.language.nb.discord_key), app_commands.Choice(value='nl', name=locale.games.hangman.params.language.nl.discord_key), app_commands.Choice(value='pl', name=locale.games.hangman.params.language.pl.discord_key), app_commands.Choice(value='pt', name=locale.games.hangman.params.language.pt.discord_key), app_commands.Choice(value='ru', name=locale.games.hangman.params.language.ru.discord_key), app_commands.Choice(value='zh', name=locale.games.hangman.params.language.zh.discord_key)])
    async def set_locale(self, interaction: discord.Interaction, locale: str) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await setLocaleCommand(command_info=command_info, locale=locale)
        return

class AdminCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        top_level_groups = [WarnCommands(name=locale.admin.warn.name.discord_key, description=locale.admin.warn.description.discord_key), RoleCommands(name=locale.admin.role.name.discord_key, description=locale.admin.role.description.discord_key), RoleManageCommands(name=locale.admin.rolemanage.name.discord_key, description=locale.admin.rolemanage.description.discord_key), ReportCommands(name=locale.admin.report.name.discord_key, description=locale.admin.report.description.discord_key), TriggerMessagesCommands(name=locale.admin.triggermessages.name.discord_key, description=locale.admin.triggermessages.description.discord_key), JoinToCreateCommands(name=locale.admin.jointocreate.name.discord_key, description=locale.admin.jointocreate.description.discord_key), AdminModerationCommands(name=locale.admin.moderation.name.discord_key, description=locale.admin.moderation.description.discord_key), AdminPurgeCommands(name=locale.admin.purgegroup.name.discord_key, description=locale.admin.purgegroup.description.discord_key), AdminChannelCommands(name=locale.admin.channels.name.discord_key, description=locale.admin.channels.description.discord_key), AdminMessagingCommands(name=locale.admin.messaging.name.discord_key, description=locale.admin.messaging.description.discord_key), AdminEmojiCommands(name=locale.admin.emoji.name.discord_key, description=locale.admin.emoji.description.discord_key), AdminSetupCommands(name=locale.admin.setup.name.discord_key, description=locale.admin.setup.description.discord_key), AdminLocaleCommands(name=locale.admin.localegroup.name.discord_key, description=locale.admin.localegroup.description.discord_key)]
        for group in top_level_groups:
            self.bot.tree.add_command(group)
AdministrationCommands = AdminModerationCommands

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))