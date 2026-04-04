from typing import cast

import discord  # type: ignore[import-not-found]
from discord import app_commands
from discord.ext import commands  # type: ignore[import-not-found]

import utility
from commands.admin.addrole import addrole as addroleCommand
from commands.admin.ban import ban as banCommand
from commands.admin.boosterrole import create_booster_role as CreateBoosterRoleCommand
from commands.admin.copy_emoji import copy_emoji as copyEmojiCommand
from commands.admin.copyrole import copyrole as copyRoleCommand
from commands.admin.createemoji import create_emoji as createEmojiCommand
from commands.admin.createrole import createrole as createroleCommand
from commands.admin.deleterole import deleterole as deleteroleCommand
from commands.admin.embedcreator import create_embed as createEmbedCommand
from commands.admin.joinToCreate.jointocreatechannel import (
    jointocreatechannel as jointoCreateChannelCommand,
)
from commands.admin.joinToCreate.removejointocreatechannel import (
    removejointocreatechannel as removeJoinToCreateChannelCommand,
)
from commands.admin.kick import kick as kickCommand
from commands.admin.lock import lock_channel as lockChannelCommand
from commands.admin.moverole import moverole as moveroleCommand
from commands.admin.nickname import change_nickname as changeNicknameCommand
from commands.admin.nuke import nuke_channel as nukeChannelCommand
from commands.admin.purge import purge as purgeCommand
from commands.admin.removerole import removerole as removeroleCommand
from commands.admin.removetimeout import remove_timeout as removeTimeoutCommand
from commands.admin.reports.remove_channel import (
    remove_channel as removeReportChannelCommand,
)
from commands.admin.reports.set_channel import set_channel as setReportChannelCommand
from commands.admin.reports.show_reports import show_reports as showReportsCommand
from commands.admin.reports.unblock_reporter import (
    unblock_reporter_cmd as unblockReporterCommand,
)
from commands.admin.say import say as sayCommand
from commands.admin.setLocale import set_locale as setLocaleCommand
from commands.admin.slowmode import set_slowmode as setSlowmodeCommand
from commands.admin.ticket.create_ticket import create_ticket as createTicketCommand
from commands.admin.timeout import timeout as timeoutCommand
from commands.admin.trigger_messages.add import (
    add_trigger_message as addTriggerMessageCommand,
)
from commands.admin.trigger_messages.configure import (
    configure_trigger_messages as configureTriggerMessagesCommand,
)
from commands.admin.unban import unban as unbanCommand
from commands.admin.unlock import unlock_channel as unlockChannelCommand
from commands.admin.viewwarns import view_warnings as viewWarningsCommand
from commands.admin.warn import warn_user as warnUserCommand
from commands.admin.warnconfig import warn_config as warnConfigCommand
from localizer import tanjunLocalizer


class WarnCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_warn_add_name"),
        description=app_commands.locale_str("admin_warn_add_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_warn_add_params_member_description"),
        reason=app_commands.locale_str("admin_warn_add_params_reason_description"),
    )
    async def add(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        user: discord.Member,
        reason: app_commands.Range[str, 0, 100] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await warnUserCommand(commandInfo=commandInfo, member=user, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_warn_view_name"),
        description=app_commands.locale_str("admin_warn_view_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_warn_view_params_member_description"),
    )
    async def view(self, interaction: discord.Interaction, user: discord.Member) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer(ephemeral=True)
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await viewWarningsCommand(commandInfo=commandInfo, member=user)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_warn_config_name"),
        description=app_commands.locale_str("admin_warn_config_description"),
    )
    async def config(self, interaction: discord.Interaction) -> None:  # type: ignore[misc,no-any-unimported]
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.response.send_modal,
            client=interaction.client,
        )

        await warnConfigCommand(commandInfo=commandInfo)
        return


class RoleCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_addrole_name"),
        description=app_commands.locale_str("admin_addrole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_addrole_params_user_name"),
        role=app_commands.locale_str("admin_addrole_params_role_name"),
    )
    async def addrole(self, interaction: discord.Interaction, user: discord.Member = None, role: discord.Role = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await addroleCommand(commandInfo=commandInfo, user=user, role=role)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_removerole_name"),
        description=app_commands.locale_str("admin_removerole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_removerole_params_user_description"),
        role=app_commands.locale_str("admin_removerole_params_role_description"),
    )
    async def removerole(  # type: ignore[misc,no-any-unimported]
        self, interaction: discord.Interaction, user: discord.Member = None, role: discord.Role = None
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await removeroleCommand(commandInfo=commandInfo, user=user, role=role)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createrole_name"),
        description=app_commands.locale_str("admin_createrole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createrole_params_name_description"),
        color=app_commands.locale_str("admin_createrole_params_color_description"),
        display_icon=app_commands.locale_str("admin_createrole_params_displayicon_description"),
        hoist=app_commands.locale_str("admin_createrole_params_hoist_description"),
        mentionable=app_commands.locale_str("admin_createrole_params_mentionable_description"),
        reason=app_commands.locale_str("admin_createrole_params_reason_description"),
        display_emoji=app_commands.locale_str("admin_createrole_params_displayemoji_description"),
    )
    async def createrole(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        name: app_commands.Range[str, 1, 100],
        color: app_commands.Range[str, 6, 7] = None,
        display_icon: discord.Attachment = None,
        hoist: bool = False,
        mentionable: bool = False,
        reason: app_commands.Range[str, 0, 100] = None,
        display_emoji: app_commands.Range[str, 0, 1] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await createroleCommand(
            commandInfo=commandInfo,
            name=name,
            color=color,
            display_icon=display_icon if display_icon else display_emoji,
            hoist=hoist,
            mentionable=mentionable,
            reason=reason,
        )
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_deleterole_name"),
        description=app_commands.locale_str("admin_deleterole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("admin_deleterole_params_role_description"),
        reason=app_commands.locale_str("admin_deleterole_params_reason_description"),
    )
    async def deleterole(  # type: ignore[misc,no-any-unimported]
        self, interaction: discord.Interaction, role: discord.Role, reason: app_commands.Range[str, 0, 100] = None
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await deleteroleCommand(commandInfo=commandInfo, role=role, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_moverole_name"),
        description=app_commands.locale_str("admin_moverole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("admin_moverole_params_role_description"),
        target_role=app_commands.locale_str("admin_moverole_params_targetrole_description"),
        position=app_commands.locale_str("admin_moverole_params_position_description"),
    )
    @app_commands.choices(  # type: ignore[untyped-decorator]
        position=[
            app_commands.Choice(
                name=app_commands.locale_str("admin_moverole_params_position_above"),
                value="above",
            ),
            app_commands.Choice(
                name=app_commands.locale_str("admin_moverole_params_position_below"),
                value="below",
            ),
        ]
    )
    async def moverole(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        role: discord.Role,
        target_role: discord.Role,
        position: app_commands.Choice[str],
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await moveroleCommand(
            commandInfo=commandInfo,
            role=role,
            target_role=target_role,
            position=position.value,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_copyrole_name"),
        description=app_commands.locale_str("admin_copyrole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("admin_copyrole_params_role_description"),
        copymembers=app_commands.locale_str("admin_copyrole_params_copymembers_description"),
    )
    @app_commands.choices(  # type: ignore[untyped-decorator]
        copymembers=[
            app_commands.Choice(
                name=app_commands.locale_str("admin_copyrole_params_copymembers_true"),
                value="true",
            ),
            app_commands.Choice(
                name=app_commands.locale_str("admin_copyrole_params_copymembers_false"),
                value="false",
            ),
        ]
    )
    async def copyrole(  # type: ignore[misc,no-any-unimported]
        self, interaction: discord.Interaction, role: discord.Role, copymembers: app_commands.Choice[str]
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await copyRoleCommand(
            commandInfo=commandInfo,
            role=role,
            copy_members=copymembers.value == "true",
        )
        return


class ReportCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_rps_setchannel_name"),
        description=app_commands.locale_str("admin_rps_setchannel_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_rps_setchannel_params_channel_description"),
    )
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = ctx.channel  # type: ignore[name-defined]

        await setReportChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_rps_removechannel_name"),
        description=app_commands.locale_str("admin_rps_removechannel_description"),
    )
    async def remove_channel(self, interaction: discord.Interaction) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await removeReportChannelCommand(commandInfo=commandInfo)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_rps_showreports_name"),
        description=app_commands.locale_str("admin_rps_showreports_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_rps_showreports_params_user_description"),
    )
    async def show_reports(self, interaction: discord.Interaction, user: discord.Member = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer(ephemeral=True)
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await showReportsCommand(commandInfo=commandInfo, user=user)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_rps_unblockreporter_name"),
        description=app_commands.locale_str("admin_rps_unblockreporter_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_rps_unblockreporter_params_user_description"),
    )
    async def unblock_reporter(self, interaction: discord.Interaction, user: discord.Member) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await unblockReporterCommand(commandInfo=commandInfo, user=user)
        return


class TriggerMessagesCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_tm_configure_name"),
        description=app_commands.locale_str("admin_tm_configure_description"),
    )
    async def configure(self, interaction: discord.Interaction) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await configureTriggerMessagesCommand(commandInfo=commandInfo)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_tm_add_name"),
        description=app_commands.locale_str("admin_tm_add_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        trigger=app_commands.locale_str("admin_tm_add_params_trigger_description"),
        response=app_commands.locale_str("admin_tm_add_params_response_description"),
        casesensitive=app_commands.locale_str("admin_tm_add_params_casesensitive_description"),
    )
    @app_commands.choices(  # type: ignore[untyped-decorator]
        casesensitive=[
            app_commands.Choice(
                name=app_commands.locale_str("admin_tm_add_params_casesensitive_true"),
                value="t",
            ),
            app_commands.Choice(
                name=app_commands.locale_str("admin_tm_add_params_casesensitive_false"),
                value="f",
            ),
        ]
    )
    async def add(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        trigger: app_commands.Range[str, 1, 128],
        response: app_commands.Range[str, 1, 1024],
        casesensitive: app_commands.Choice[str] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await addTriggerMessageCommand(
            commandInfo=commandInfo,
            trigger=trigger,
            response=response,
            caseSensitive=casesensitive.value == "t" if casesensitive else False,
        )
        return


class JoinToCreateCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_jtc_setchannel_name"),
        description=app_commands.locale_str("admin_jtc_setchannel_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_jtc_setchannel_params_channel_description"),
    )
    async def set_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await jointoCreateChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_jtc_removechannel_name"),
        description=app_commands.locale_str("admin_jtc_removechannel_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_jtc_removechannel_params_channel_description"),
    )
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.VoiceChannel) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await removeJoinToCreateChannelCommand(commandInfo=commandInfo, channel=channel)
        return


class administrationCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_kick_name"),
        description=app_commands.locale_str("admin_kick_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_kick_params_user_description"),
        reason=app_commands.locale_str("admin_kick_params_reason_description"),
    )
    async def kick(  # type: ignore[misc,no-any-unimported]
        self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 0, 100] = None
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await kickCommand(commandInfo=commandInfo, target=user, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_ban_name"),
        description=app_commands.locale_str("admin_ban_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_ban_params_user_description"),
        reason=app_commands.locale_str("admin_ban_params_reason_description"),
        delete_message_days=app_commands.locale_str("admin_ban_params_deletemessagedays_description"),
    )
    async def ban(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        user: discord.Member,
        reason: app_commands.Range[str, 0, 100] = None,
        delete_message_days: app_commands.Range[int, 0, 7] = 0,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await banCommand(
            commandInfo=commandInfo,
            target=user,
            reason=reason,
            delete_message_days=delete_message_days,
        )
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_unban_name"),
        description=app_commands.locale_str("admin_unban_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        username=app_commands.locale_str("admin_unban_params_username_description"),
        reason=app_commands.locale_str("admin_unban_params_reason_description"),
    )
    async def unban(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        username: app_commands.Range[str, 1, 100],
        reason: app_commands.Range[str, 0, 100] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await unbanCommand(commandInfo=commandInfo, username=username, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_timeout_name"),
        description=app_commands.locale_str("admin_timeout_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_timeout_params_member_description"),
        duration=app_commands.locale_str("admin_timeout_params_duration_description"),
        reason=app_commands.locale_str("admin_timeout_params_reason_description"),
    )
    async def timeout(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        user: discord.Member,
        duration: app_commands.Range[int, 1, 40320],
        reason: app_commands.Range[str, 0, 100] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await timeoutCommand(commandInfo=commandInfo, member=user, duration=duration, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_removetimeout_name"),
        description=app_commands.locale_str("admin_removetimeout_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_removetimeout_params_member_description"),
        reason=app_commands.locale_str("admin_removetimeout_params_reason_description"),
    )
    async def removetimeout(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        user: discord.Member,
        reason: app_commands.Range[str, 0, 100] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await removeTimeoutCommand(commandInfo=commandInfo, member=user, reason=reason)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_purge_name"),
        description=app_commands.locale_str("admin_purge_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        limit=app_commands.locale_str("admin_purge_params_amount_description"),
        channel=app_commands.locale_str("admin_purge_params_channel_description"),
        setting=app_commands.locale_str("admin_purge_params_setting_description"),
    )
    @app_commands.choices(  # type: ignore[untyped-decorator]
        setting=[
            app_commands.Choice(
                value="all",
                name=app_commands.locale_str("admin_purge_params_setting_all"),
            ),
            app_commands.Choice(
                value="bot",
                name=app_commands.locale_str("admin_purge_params_setting_bot"),
            ),
            app_commands.Choice(
                value="user",
                name=app_commands.locale_str("admin_purge_params_setting_user"),
            ),
            app_commands.Choice(
                value="notPinned",
                name=app_commands.locale_str("admin_purge_params_setting_notPinned"),
            ),
            app_commands.Choice(
                value="userNotPinned",
                name=app_commands.locale_str("admin_purge_params_setting_userNotPinned"),
            ),
            app_commands.Choice(
                value="botNotPinned",
                name=app_commands.locale_str("admin_purge_params_setting_botNotPinned"),
            ),
            app_commands.Choice(
                value="notadmin",
                name=app_commands.locale_str("admin_purge_params_setting_notAdmin"),
            ),
            app_commands.Choice(
                value="notUserAdmin",
                name=app_commands.locale_str("admin_purge_params_setting_notUserAdmin"),
            ),
            app_commands.Choice(
                value="embeds",
                name=app_commands.locale_str("admin_purge_params_setting_embeds"),
            ),
            app_commands.Choice(
                value="files",
                name=app_commands.locale_str("admin_purge_params_setting_files"),
            ),
            app_commands.Choice(
                value="notAdminNotPinned",
                name=app_commands.locale_str("admin_purge_params_setting_notAdminNotPinned"),
            ),
        ]
    )
    async def purge(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        limit: app_commands.Range[int, 1, 1000],
        channel: discord.TextChannel = None,
        setting: app_commands.Choice[str] = "all",
    ) -> None:
        await interaction.response.defer(ephemeral=True)  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await purgeCommand(
            commandInfo=commandInfo,
            amount=limit,
            channel=channel,
            setting=setting.value if setting != "all" else "all",
        )
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_nickname_name"),
        description=app_commands.locale_str("admin_nickname_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("admin_nickname_params_member_description"),
        nickname=app_commands.locale_str("admin_nickname_params_nickname_description"),
    )
    async def nickname(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        user: discord.Member,
        nickname: app_commands.Range[str, 0, 100] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await changeNicknameCommand(commandInfo=commandInfo, member=user, nickname=nickname)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_slowmode_name"),
        description=app_commands.locale_str("admin_slowmode_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        seconds=app_commands.locale_str("admin_slowmode_params_seconds_description"),
        channel=app_commands.locale_str("admin_slowmode_params_channel_description"),
    )
    async def slowmode(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        seconds: app_commands.Range[int, 1, 21600],
        channel: discord.TextChannel = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        await setSlowmodeCommand(commandInfo=commandInfo, seconds=seconds, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_lock_name"),
        description=app_commands.locale_str("admin_lock_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_lock_params_channel_description"),
    )
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await lockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_unlock_name"),
        description=app_commands.locale_str("admin_unlock_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_unlock_params_channel_description"),
    )
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await unlockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_nuke_name"),
        description=app_commands.locale_str("admin_nuke_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_nuke_params_channel_description"),
    )
    async def nuke(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = ctx.channel  # type: ignore[name-defined]

        await nukeChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_say_name"),
        description=app_commands.locale_str("admin_say_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("admin_say_params_channel_description"),
        message=app_commands.locale_str("admin_say_params_message_description"),
    )
    async def say(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        message: app_commands.Range[str, 1, 2000],
        channel: discord.TextChannel = None,
    ) -> None:
        await interaction.response.defer(ephemeral=True)  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        if not channel:
            channel = ctx.channel

        await sayCommand(commandInfo=commandInfo, channel=channel, message=message)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_embed_name"),
        description=app_commands.locale_str("admin_embed_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        title=app_commands.locale_str("admin_embed_params_title_description"),
        channel=app_commands.locale_str("admin_embed_params_channel_description"),
    )
    async def embed(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        title: app_commands.Range[str, 1, 256],
        channel: discord.TextChannel = None,
    ) -> None:
        await interaction.response.defer(ephemeral=True)  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        if channel is None:
            channel = ctx.channel

        await createEmbedCommand(commandInfo=commandInfo, channel=channel, title=title)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createemoji_name"),
        description=app_commands.locale_str("admin_createemoji_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createemoji_params_name_description"),
        imageurl=app_commands.locale_str("admin_createemoji_params_imageUrl_description"),
    )
    async def createemoji(self, interaction: discord.Interaction, name: str, imageurl: str) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        view = discord.ui.View()
        role_select = discord.ui.RoleSelect(
            placeholder=tanjunLocalizer.localize(ctx.locale, "commands.admin.createEmoji.roleSelectPlaceholder"),  # type: ignore[name-defined]
            default_values=[ctx.guild.default_role],  # type: ignore[name-defined]
            min_values=1,
            max_values=25,
        )

        async def role_select_callback(interaction: discord.Interaction) -> None:  # type: ignore[no-any-unimported]
            roles = [ctx.guild.get_role(int(r)) for r in interaction.data["values"]]  # type: ignore[name-defined]
            commandInfo.message = interaction.message
            commandInfo.reply = interaction.response.send_message
            await createEmojiCommand(commandInfo=commandInfo, name=name, image_url=imageurl, roles=roles)

        role_select.callback = role_select_callback
        view.add_item(role_select)
        await ctx.followup.send(  # type: ignore[name-defined]
            tanjunLocalizer.localize(ctx.locale, "commands.admin.createEmoji.roleSelect"),  # type: ignore[name-defined]
            view=view,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_boosterrole_name"),
        description=app_commands.locale_str("admin_boosterrole_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("admin_boosterrole_params_role_description"),
    )
    async def claimboosterrole(self, interaction: discord.Interaction, role: discord.Role = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )
        await CreateBoosterRoleCommand(commandInfo=commandInfo, role=role)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createticket_name"),
        description=app_commands.locale_str("admin_createticket_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_createticket_params_name_description"),
        description=app_commands.locale_str("admin_createticket_params_description_description"),
        channel=app_commands.locale_str("admin_createticket_params_channel_description"),
        pingrole=app_commands.locale_str("admin_createticket_params_pingrole_description"),
        summarychannel=app_commands.locale_str("admin_createticket_params_summarychannel_description"),
        introduction=app_commands.locale_str("admin_createticket_params_introduction_description"),
    )
    async def create_ticket(  # type: ignore[misc,no-any-unimported,no-untyped-def]
        self,
        ctx,
        name: app_commands.Range[str, 1, 128],
        description: app_commands.Range[str, 1, 1024],
        channel: discord.TextChannel = None,
        pingrole: discord.Role = None,
        summarychannel: discord.TextChannel = None,
        introduction: app_commands.Range[str, 0, 1024] = None,
    ) -> None:
        await interaction.response.defer()  # type: ignore[name-defined]
        commandInfo = utility.CommandInfo(
            user=interaction.user,  # type: ignore[name-defined]
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[name-defined,no-any-unimported]
            guild=interaction.guild,  # type: ignore[name-defined]
            command=interaction.command,  # type: ignore[name-defined]
            locale=interaction.locale,  # type: ignore[name-defined]
            message=interaction.message,  # type: ignore[name-defined]
            permissions=interaction.permissions,  # type: ignore[name-defined]
            reply=interaction.followup.send,  # type: ignore[name-defined]
            client=interaction.client,  # type: ignore[name-defined]
        )

        if not channel:
            channel = ctx.channel

        await createTicketCommand(
            commandInfo=commandInfo,
            channel=channel,
            name=name,
            description=description,
            ping_role=pingrole,
            summary_channel=summarychannel,
            introduction=introduction,
        )
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_setlocale_name"),
        description=app_commands.locale_str("admin_setlocale_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        locale=app_commands.locale_str("admin_setlocale_params_locale_description"),
    )
    @app_commands.choices(  # type: ignore[untyped-decorator]
        locale=[
            app_commands.Choice(
                value="bg",
                name=app_commands.locale_str("games_hangman_params_language_bg"),
            ),
            app_commands.Choice(
                value="cs",
                name=app_commands.locale_str("games_hangman_params_language_cs"),
            ),
            app_commands.Choice(
                value="da",
                name=app_commands.locale_str("games_hangman_params_language_da"),
            ),
            app_commands.Choice(
                value="de",
                name=app_commands.locale_str("games_hangman_params_language_de"),
            ),
            app_commands.Choice(
                value="el",
                name=app_commands.locale_str("games_hangman_params_language_el"),
            ),
            app_commands.Choice(
                value="en",
                name=app_commands.locale_str("games_hangman_params_language_en"),
            ),
            app_commands.Choice(
                value="es",
                name=app_commands.locale_str("games_hangman_params_language_es"),
            ),
            app_commands.Choice(
                value="fi",
                name=app_commands.locale_str("games_hangman_params_language_fi"),
            ),
            app_commands.Choice(
                value="fr",
                name=app_commands.locale_str("games_hangman_params_language_fr"),
            ),
            app_commands.Choice(
                value="hi",
                name=app_commands.locale_str("games_hangman_params_language_hi"),
            ),
            app_commands.Choice(
                value="hu",
                name=app_commands.locale_str("games_hangman_params_language_hu"),
            ),
            app_commands.Choice(
                value="id",
                name=app_commands.locale_str("games_hangman_params_language_id"),
            ),
            app_commands.Choice(
                value="it",
                name=app_commands.locale_str("games_hangman_params_language_it"),
            ),
            app_commands.Choice(
                value="ja",
                name=app_commands.locale_str("games_hangman_params_language_ja"),
            ),
            app_commands.Choice(
                value="ko",
                name=app_commands.locale_str("games_hangman_params_language_ko"),
            ),
            app_commands.Choice(
                value="lt",
                name=app_commands.locale_str("games_hangman_params_language_lt"),
            ),
            app_commands.Choice(
                value="nb",
                name=app_commands.locale_str("games_hangman_params_language_nb"),
            ),
            app_commands.Choice(
                value="nl",
                name=app_commands.locale_str("games_hangman_params_language_nl"),
            ),
            app_commands.Choice(
                value="pl",
                name=app_commands.locale_str("games_hangman_params_language_pl"),
            ),
            app_commands.Choice(
                value="pt",
                name=app_commands.locale_str("games_hangman_params_language_pt"),
            ),
            app_commands.Choice(
                value="ru",
                name=app_commands.locale_str("games_hangman_params_language_ru"),
            ),
            app_commands.Choice(
                value="zh",
                name=app_commands.locale_str("games_hangman_params_language_zh"),
            ),
        ]
    )
    async def set_locale(self, interaction: discord.Interaction, locale: str) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await setLocaleCommand(commandInfo=commandInfo, locale=locale)
        return

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("admin_copyemoji_name"),
        description=app_commands.locale_str("admin_copyemoji_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        emoji=app_commands.locale_str("admin_copyemoji_params_emoji_description"),
    )
    async def copy_emoji(self, interaction: discord.Interaction, emoji: str) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )
        await copyEmojiCommand(commandInfo=commandInfo, emoji=emoji)
        return


class adminCog(commands.Cog):  # type: ignore[misc,no-any-unimported]
    def __init__(self, bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
        self.bot = bot

    @commands.Cog.listener()  # type: ignore[untyped-decorator]
    async def on_ready(self) -> None:  # type: ignore[misc]
        admincmds = administrationCommands(
            name=app_commands.locale_str("admin_name"),
            description=app_commands.locale_str("admin_description"),
        )
        warncmds = WarnCommands(
            name=app_commands.locale_str("admin_warn_name"),
            description=app_commands.locale_str("admin_warn_description"),
        )
        admincmds.add_command(warncmds)
        rolecmds = RoleCommands(
            name=app_commands.locale_str("admin_role_name"),
            description=app_commands.locale_str("admin_role_description"),
        )
        admincmds.add_command(rolecmds)
        reportcmds = ReportCommands(
            name=app_commands.locale_str("admin_report_name"),
            description=app_commands.locale_str("admin_report_description"),
        )
        admincmds.add_command(reportcmds)
        trigger_messages_cmds = TriggerMessagesCommands(
            name=app_commands.locale_str("admin_triggermessages_name"),
            description=app_commands.locale_str("admin_triggermessages_description"),
        )
        admincmds.add_command(trigger_messages_cmds)
        join_to_create_cmds = JoinToCreateCommands(
            name=app_commands.locale_str("admin_jointocreate_name"),
            description=app_commands.locale_str("admin_jointocreate_description"),
        )
        admincmds.add_command(join_to_create_cmds)
        self.bot.tree.add_command(admincmds)


async def setup(bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
    await bot.add_cog(adminCog(bot))
