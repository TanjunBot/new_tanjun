import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.admin.addrole import addrole as addroleCommand
from commands.admin.removerole import removerole as removeroleCommand
from commands.admin.createrole import createrole as createroleCommand
from commands.admin.deleterole import deleterole as deleteroleCommand
from commands.admin.kick import kick as kickCommand
from commands.admin.ban import ban as banCommand
from commands.admin.unban import unban as unbanCommand
from commands.admin.timeout import timeout as timeoutCommand
from commands.admin.removetimeout import remove_timeout as removeTimeoutCommand
from commands.admin.purge import purge as purgeCommand
from commands.admin.nickname import change_nickname as changeNicknameCommand
from commands.admin.slowmode import set_slowmode as setSlowmodeCommand
from commands.admin.lock import lock_channel as lockChannelCommand
from commands.admin.unlock import unlock_channel as unlockChannelCommand
from commands.admin.nuke import nuke_channel as nukeChannelCommand
from commands.admin.say import say as sayCommand
from commands.admin.embedcreator import create_embed as createEmbedCommand
from commands.admin.createemoji import create_emoji as createEmojiCommand
from commands.admin.warn import warn_user as warnUserCommand
from commands.admin.viewwarns import view_warnings as viewWarningsCommand
from commands.admin.warnconfig import warn_config as warnConfigCommand
from commands.admin.moverole import moverole as moveroleCommand
from commands.admin.boosterrole import create_booster_role as CreateBoosterRoleCommand
from commands.admin.copyrole import copyrole as copyRoleCommand
from commands.admin.reports.set_channel import set_channel as setReportChannelCommand
from commands.admin.reports.remove_channel import (
    remove_channel as removeReportChannelCommand,
)
from commands.admin.reports.show_reports import show_reports as showReportsCommand
from commands.admin.trigger_messages.configure import (
    configure_trigger_messages as configureTriggerMessagesCommand,
)
from commands.admin.trigger_messages.add import (
    add_trigger_message as addTriggerMessageCommand,
)

from commands.admin.ticket.create_ticket import create_ticket as createTicketCommand
from commands.admin.joinToCreate.jointocreatechannel import (
    jointocreatechannel as jointoCreateChannelCommand,
)
from commands.admin.joinToCreate.removejointocreatechannel import (
    removejointocreatechannel as removeJoinToCreateChannelCommand,
)
from commands.admin.setLocale import set_locale as setLocaleCommand


class WarnCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_warn_add_name"),
        description=app_commands.locale_str("admin_warn_add_description"),
    )
    @app_commands.describe(
        member=app_commands.locale_str("admin_warn_add_params_member_description"),
        reason=app_commands.locale_str("admin_warn_add_params_reason_description"),
    )
    async def add(self, ctx, member: discord.Member, reason: str = None):
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

        await warnUserCommand(commandInfo=commandInfo, member=member, reason=reason)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_warn_view_name"),
        description=app_commands.locale_str("admin_warn_view_description"),
    )
    @app_commands.describe(
        member=app_commands.locale_str("admin_warn_view_params_member_description"),
    )
    async def view(self, ctx, member: discord.Member):
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

        await viewWarningsCommand(commandInfo=commandInfo, member=member)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_warn_config_name"),
        description=app_commands.locale_str("admin_warn_config_description"),
    )
    async def config(self, ctx):
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.response.send_modal,
            client=ctx.client,
        )

        await warnConfigCommand(commandInfo=commandInfo)
        return


class RoleCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_addrole_name"),
        description=app_commands.locale_str("admin_addrole_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_addrole_params_user_name"),
        role=app_commands.locale_str("admin_addrole_params_role_name"),
    )
    async def addrole(
        self, ctx, user: discord.Member = None, role: discord.Role = None
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

        await addroleCommand(commandInfo=commandInfo, user=user, role=role)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_removerole_name"),
        description=app_commands.locale_str("admin_removerole_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_removerole_params_user_description"),
        role=app_commands.locale_str("admin_removerole_params_role_description"),
    )
    async def removerole(
        self, ctx, user: discord.Member = None, role: discord.Role = None
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

        await removeroleCommand(commandInfo=commandInfo, user=user, role=role)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_createrole_name"),
        description=app_commands.locale_str("admin_createrole_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("admin_createrole_params_name_description"),
        color=app_commands.locale_str("admin_createrole_params_color_description"),
        display_icon=app_commands.locale_str(
            "admin_createrole_params_displayicon_description"
        ),
        hoist=app_commands.locale_str("admin_createrole_params_hoist_description"),
        mentionable=app_commands.locale_str(
            "admin_createrole_params_mentionable_description"
        ),
        reason=app_commands.locale_str("admin_createrole_params_reason_description"),
        display_emoji=app_commands.locale_str(
            "admin_createrole_params_displayemoji_description"
        ),
    )
    async def createrole(
        self,
        ctx,
        name: str,
        color: str = None,
        display_icon: discord.Attachment = None,
        hoist: bool = False,
        mentionable: bool = False,
        reason: str = None,
        display_emoji: str = None,
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

    @app_commands.command(
        name=app_commands.locale_str("admin_deleterole_name"),
        description=app_commands.locale_str("admin_deleterole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("admin_deleterole_params_role_description"),
        reason=app_commands.locale_str("admin_deleterole_params_reason_description"),
    )
    async def deleterole(self, ctx, role: discord.Role, reason: str = None):
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

        await deleteroleCommand(commandInfo=commandInfo, role=role, reason=reason)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_moverole_name"),
        description=app_commands.locale_str("admin_moverole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("admin_moverole_params_role_description"),
        target_role=app_commands.locale_str(
            "admin_moverole_params_targetrole_description"
        ),
        position=app_commands.locale_str("admin_moverole_params_position_description"),
    )
    @app_commands.choices(
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
    async def moverole(
        self,
        ctx,
        role: discord.Role,
        target_role: discord.Role,
        position: app_commands.Choice[str],
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

        await moveroleCommand(
            commandInfo=commandInfo,
            role=role,
            target_role=target_role,
            position=position.value,
        )

    @app_commands.command(
        name=app_commands.locale_str("admin_copyrole_name"),
        description=app_commands.locale_str("admin_copyrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("admin_copyrole_params_role_description"),
        copymembers=app_commands.locale_str(
            "admin_copyrole_params_copymembers_description"
        ),
    )
    @app_commands.choices(
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
    async def copyrole(
        self, ctx, role: discord.Role, copymembers: app_commands.Choice[str]
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

        await copyRoleCommand(
            commandInfo=commandInfo,
            role=role,
            copy_members=copymembers.value == "true",
        )
        return


class ReportCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_rps_setchannel_name"),
        description=app_commands.locale_str("admin_rps_setchannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "admin_rps_setchannel_params_channel_description"
        ),
    )
    async def set_channel(self, ctx, channel: discord.TextChannel = None):
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

        await setReportChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_rps_removechannel_name"),
        description=app_commands.locale_str("admin_rps_removechannel_description"),
    )
    async def remove_channel(self, ctx):
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

        await removeReportChannelCommand(commandInfo=commandInfo)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_rps_showreports_name"),
        description=app_commands.locale_str("admin_rps_showreports_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_rps_showreports_params_user_description"),
    )
    async def show_reports(self, ctx, user: discord.Member = None):
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

        await showReportsCommand(commandInfo=commandInfo, user=user)
        return


class TriggerMessagesCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_tm_configure_name"),
        description=app_commands.locale_str("admin_tm_configure_description"),
    )
    async def configure(self, ctx):
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

        await configureTriggerMessagesCommand(commandInfo=commandInfo)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_tm_add_name"),
        description=app_commands.locale_str("admin_tm_add_description"),
    )
    @app_commands.describe(
        trigger=app_commands.locale_str("admin_tm_add_params_trigger_description"),
        response=app_commands.locale_str("admin_tm_add_params_response_description"),
        casesensitive=app_commands.locale_str(
            "admin_tm_add_params_casesensitive_description"
        ),
    )
    @app_commands.choices(
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
    async def add(
        self,
        ctx,
        trigger: str,
        response: str,
        casesensitive: app_commands.Choice[str] = None,
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

        await addTriggerMessageCommand(
            commandInfo=commandInfo,
            trigger=trigger,
            response=response,
            caseSensitive=casesensitive.value == "t" if casesensitive else False,
        )
        return


class JoinToCreateCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_jtc_setchannel_name"),
        description=app_commands.locale_str("admin_jtc_setchannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "admin_jtc_setchannel_params_channel_description"
        ),
    )
    async def set_channel(self, ctx, channel: discord.VoiceChannel):
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

        await jointoCreateChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_jtc_removechannel_name"),
        description=app_commands.locale_str("admin_jtc_removechannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "admin_jtc_removechannel_params_channel_description"
        ),
    )
    async def remove_channel(self, ctx, channel: discord.VoiceChannel):
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

        await removeJoinToCreateChannelCommand(commandInfo=commandInfo, channel=channel)
        return


class administrationCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_kick_name"),
        description=app_commands.locale_str("admin_kick_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_kick_params_user_description"),
        reason=app_commands.locale_str("admin_kick_params_reason_description"),
    )
    async def kick(self, ctx, user: discord.Member, reason: str = None):
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

        await kickCommand(commandInfo=commandInfo, target=user, reason=reason)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_ban_name"),
        description=app_commands.locale_str("admin_ban_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_ban_params_user_description"),
        reason=app_commands.locale_str("admin_ban_params_reason_description"),
        delete_message_days=app_commands.locale_str(
            "admin_ban_params_deletemessagedays_description"
        ),
    )
    async def ban(
        self,
        ctx,
        user: discord.Member,
        reason: str = None,
        delete_message_days: int = 0,
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

        await banCommand(
            commandInfo=commandInfo,
            target=user,
            reason=reason,
            delete_message_days=delete_message_days,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_unban_name"),
        description=app_commands.locale_str("admin_unban_description"),
    )
    @app_commands.describe(
        username=app_commands.locale_str("admin_unban_params_username_description"),
        reason=app_commands.locale_str("admin_unban_params_reason_description"),
    )
    async def unban(self, ctx, username: str, reason: str = None):
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

        await unbanCommand(commandInfo=commandInfo, username=username, reason=reason)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_timeout_name"),
        description=app_commands.locale_str("admin_timeout_description"),
    )
    @app_commands.describe(
        member=app_commands.locale_str("admin_timeout_params_member_description"),
        duration=app_commands.locale_str("admin_timeout_params_duration_description"),
        reason=app_commands.locale_str("admin_timeout_params_reason_description"),
    )
    async def timeout(
        self, ctx, member: discord.Member, duration: int, reason: str = None
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

        await timeoutCommand(
            commandInfo=commandInfo, member=member, duration=duration, reason=reason
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_removetimeout_name"),
        description=app_commands.locale_str("admin_removetimeout_description"),
    )
    @app_commands.describe(
        member=app_commands.locale_str("admin_removetimeout_params_member_description"),
        reason=app_commands.locale_str("admin_removetimeout_params_reason_description"),
    )
    async def removetimeout(self, ctx, member: discord.Member, reason: str = None):
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

        await removeTimeoutCommand(
            commandInfo=commandInfo, member=member, reason=reason
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_purge_name"),
        description=app_commands.locale_str("admin_purge_description"),
    )
    @app_commands.describe(
        limit=app_commands.locale_str("admin_purge_params_amount_description"),
        channel=app_commands.locale_str("admin_purge_params_channel_description"),
        setting=app_commands.locale_str("admin_purge_params_setting_description"),
    )
    @app_commands.choices(
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
                name=app_commands.locale_str(
                    "admin_purge_params_setting_userNotPinned"
                ),
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
                name=app_commands.locale_str(
                    "admin_purge_params_setting_notAdminNotPinned"
                ),
            ),
        ]
    )
    async def purge(
        self,
        ctx,
        limit: int,
        channel: discord.TextChannel = None,
        setting: app_commands.Choice[str] = "all",
    ):
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

        await purgeCommand(
            commandInfo=commandInfo,
            amount=limit,
            channel=channel,
            setting=setting.value if setting != "all" else "all",
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_nickname_name"),
        description=app_commands.locale_str("admin_nickname_description"),
    )
    @app_commands.describe(
        member=app_commands.locale_str("admin_nickname_params_member_description"),
        nickname=app_commands.locale_str("admin_nickname_params_nickname_description"),
    )
    async def nickname(self, ctx, member: discord.Member, nickname: str = None):
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

        await changeNicknameCommand(
            commandInfo=commandInfo, member=member, nickname=nickname
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_slowmode_name"),
        description=app_commands.locale_str("admin_slowmode_description"),
    )
    @app_commands.describe(
        seconds=app_commands.locale_str("admin_slowmode_params_seconds_description"),
        channel=app_commands.locale_str("admin_slowmode_params_channel_description"),
    )
    async def slowmode(self, ctx, seconds: int, channel: discord.TextChannel = None):
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

        await setSlowmodeCommand(
            commandInfo=commandInfo, seconds=seconds, channel=channel
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_lock_name"),
        description=app_commands.locale_str("admin_lock_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("admin_lock_params_channel_description"),
    )
    async def lock(self, ctx, channel: discord.TextChannel = None):
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

        await lockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_unlock_name"),
        description=app_commands.locale_str("admin_unlock_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("admin_unlock_params_channel_description"),
    )
    async def unlock(self, ctx, channel: discord.TextChannel = None):
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

        await unlockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_nuke_name"),
        description=app_commands.locale_str("admin_nuke_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("admin_nuke_params_channel_description"),
    )
    async def nuke(self, ctx, channel: discord.TextChannel = None):
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

        await nukeChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_say_name"),
        description=app_commands.locale_str("admin_say_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("admin_say_params_channel_description"),
        message=app_commands.locale_str("admin_say_params_message_description"),
    )
    async def say(self, ctx, message: str, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await sayCommand(commandInfo=commandInfo, channel=channel, message=message)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_embed_name"),
        description=app_commands.locale_str("admin_embed_description"),
    )
    @app_commands.describe(
        title=app_commands.locale_str("admin_embed_params_title_description"),
        channel=app_commands.locale_str("admin_embed_params_channel_description"),
    )
    async def embed(
        self,
        ctx,
        title: app_commands.Range[str, 1, 256],
        channel: discord.TextChannel = None,
    ):
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

        if channel is None:
            channel = ctx.channel

        await createEmbedCommand(commandInfo=commandInfo, channel=channel, title=title)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_createemoji_name"),
        description=app_commands.locale_str("admin_createemoji_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("admin_createemoji_params_name_description"),
        imageurl=app_commands.locale_str(
            "admin_createemoji_params_imageUrl_description"
        ),
    )
    async def createemoji(self, ctx, name: str, imageurl: str):
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

        view = discord.ui.View()
        role_select = discord.ui.RoleSelect(
            placeholder=tanjunLocalizer.localize(
                ctx.locale, "commands.admin.createEmoji.roleSelectPlaceholder"
            ),
            default_values=[ctx.guild.default_role],
            min_values=1,
            max_values=25,
        )

        async def role_select_callback(interaction: discord.Interaction):
            roles = [ctx.guild.get_role(int(r)) for r in interaction.data["values"]]
            commandInfo.message = interaction.message
            commandInfo.reply = interaction.response.send_message
            await createEmojiCommand(
                commandInfo=commandInfo, name=name, image_url=imageurl, roles=roles
            )

        role_select.callback = role_select_callback
        view.add_item(role_select)
        await ctx.followup.send(
            tanjunLocalizer.localize(
                ctx.locale, "commands.admin.createEmoji.roleSelect"
            ),
            view=view,
        )

    @app_commands.command(
        name=app_commands.locale_str("admin_boosterrole_name"),
        description=app_commands.locale_str("admin_boosterrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("admin_boosterrole_params_role_description"),
    )
    async def claimboosterrole(self, ctx, role: discord.Role = None):
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
        await CreateBoosterRoleCommand(commandInfo=commandInfo, role=role)

    @app_commands.command(
        name=app_commands.locale_str("admin_createticket_name"),
        description=app_commands.locale_str("admin_createticket_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("admin_createticket_params_name_description"),
        description=app_commands.locale_str(
            "admin_createticket_params_description_description"
        ),
        channel=app_commands.locale_str(
            "admin_createticket_params_channel_description"
        ),
        pingrole=app_commands.locale_str(
            "admin_createticket_params_pingrole_description"
        ),
        summarychannel=app_commands.locale_str(
            "admin_createticket_params_summarychannel_description"
        ),
        introduction=app_commands.locale_str(
            "admin_createticket_params_introduction_description"
        ),
    )
    async def create_ticket(
        self,
        ctx,
        name: str,
        description: str,
        channel: discord.TextChannel = None,
        pingrole: discord.Role = None,
        summarychannel: discord.TextChannel = None,
        introduction: str = None,
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

    @app_commands.command(
        name=app_commands.locale_str("admin_setlocale_name"),
        description=app_commands.locale_str("admin_setlocale_description"),
    )
    @app_commands.describe(
        locale=app_commands.locale_str("admin_setlocale_params_locale_description"),
    )
    @app_commands.choices(
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
    async def set_locale(self, ctx, locale: str):
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

        await setLocaleCommand(commandInfo=commandInfo, locale=locale)
        return


class adminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addrole(self, ctx, **args) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        target: discord.Member = ctx.message.mentions

        if len(target) == 0:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.addrole.noUser",
                )
            )
            return

        role: discord.Role = ctx.message.role_mentions
        if len(role) == 0:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.addrole.noRole",
                )
            )
            return
        for t in target:
            for r in role:
                await addroleCommand(commandInfo=commandInfo, target=t, role=r)
        return

    @commands.command()
    async def removerole(self, ctx) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        target = ctx.message.mentions
        if len(target) == 0:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.removerole.noUser",
                )
            )
            return

        role = ctx.message.role_mentions
        if len(role) == 0:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.removerole.noRole",
                )
            )
            return

        for t in target:
            for r in role:
                await removeroleCommand(commandInfo=commandInfo, target=t, role=r)

        return

    @commands.command()
    async def createrole(
        self,
        ctx,
        name: str,
        color: str = None,
        hoist: bool = False,
        mentionable: bool = False,
        emoji: str = None,
    ):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        if not name:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.createrole.noName",
                )
            )
            return

        display_icon = None
        if ctx.message.attachments:
            display_icon = await ctx.message.attachments[0].read()
        elif emoji:
            display_icon = emoji

        await createroleCommand(
            commandInfo=commandInfo,
            name=name,
            color=color,
            hoist=hoist,
            mentionable=mentionable,
            display_icon=display_icon,
        )
        return

    @commands.command()
    async def deleterole(self, ctx) -> None:
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        role = ctx.message.role_mentions
        if len(role) == 0:
            await ctx.reply(
                tanjunLocalizer.localize(
                    locale=(
                        ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US"
                    ),
                    key="commands.admin.deleterole.noRole",
                )
            )
            return

        for r in role:
            await deleteroleCommand(commandInfo=commandInfo, role=r)

        return

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await kickCommand(commandInfo=commandInfo, target=member, reason=reason)
        return

    @commands.command()
    async def ban(
        self,
        ctx,
        member: discord.Member,
        delete_message_days: int = 0,
        *,
        reason: str = None
    ):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await banCommand(
            commandInfo=commandInfo,
            target=member,
            reason=reason,
            delete_message_days=delete_message_days,
        )
        return

    @commands.command()
    async def unban(self, ctx, username: str, *, reason: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await unbanCommand(commandInfo=commandInfo, username=username, reason=reason)
        return

    @commands.command()
    async def timeout(
        self, ctx, member: discord.Member, duration: int, *, reason: str = None
    ):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await timeoutCommand(
            commandInfo=commandInfo, member=member, duration=duration, reason=reason
        )
        return

    @commands.command()
    async def untimeout(self, ctx, member: discord.Member, *, reason: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await removeTimeoutCommand(
            commandInfo=commandInfo, member=member, reason=reason
        )
        return

    @commands.command()
    async def purge(self, ctx, amount: int, channel: discord.TextChannel = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await purgeCommand(
            commandInfo=commandInfo, amount=amount, channel=channel, setting="all"
        )
        return

    @commands.command()
    async def nickname(self, ctx, member: discord.Member, *, nickname: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await changeNicknameCommand(
            commandInfo=commandInfo, member=member, nickname=nickname
        )
        return

    @commands.command()
    async def slowmode(self, ctx, seconds: int, channel: discord.TextChannel = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await setSlowmodeCommand(
            commandInfo=commandInfo, seconds=seconds, channel=channel
        )
        return

    @commands.command()
    async def lock(self, ctx, channel: discord.TextChannel = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await lockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @commands.command()
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await unlockChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await warnUserCommand(commandInfo=commandInfo, member=member, reason=reason)
        return

    @commands.command()
    async def viewwarns(self, ctx, member: discord.Member):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await viewWarningsCommand(commandInfo=commandInfo, member=member)
        return

    @commands.command()
    async def nuke(self, ctx, channel: discord.TextChannel = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        if not channel:
            channel = ctx.channel

        await nukeChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @commands.command()
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await sayCommand(commandInfo=commandInfo, channel=channel, message=message)
        return

    @commands.command()
    async def embed(self, ctx, channel: discord.TextChannel, *, title: str):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        if channel is None:
            channel = ctx.channel

        if not title:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.embed.missingTitle.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.embed.missingTitle.description",
                ),
            )
            await ctx.reply(embed=embed)
            return

        await createEmbedCommand(commandInfo=commandInfo, channel=channel, title=title)
        return

    @commands.command()
    async def createemoji(self, ctx, name: str, image_url: str, *roles: discord.Role):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await createEmojiCommand(
            commandInfo=commandInfo, name=name, image_url=image_url, roles=list(roles)
        )

    @commands.command()
    async def claimboosterrole(self, ctx, role: discord.Role = None):
        commandInfo = utility.commandInfo(
            user=ctx.author,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.guild.locale if hasattr(ctx.guild, "locale") else "en_US",
            message=ctx.message,
            permissions=ctx.author.guild_permissions,
            reply=ctx.reply,
            client=ctx.bot,
        )

        await CreateBoosterRoleCommand(commandInfo=commandInfo, role=role)

    @commands.Cog.listener()
    async def on_ready(self):
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


async def setup(bot):
    await bot.add_cog(adminCog(bot))
