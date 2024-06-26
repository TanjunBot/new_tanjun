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

class administrationCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("admin_addrole_name"),
        description=app_commands.locale_str("admin_addrole_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_addrole_params_user_name"),
        role=app_commands.locale_str("admin_addrole_params_role_name"),
    )
    async def addrole(self, ctx, user: discord.Member, role: discord.Role):
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

        await addroleCommand(commandInfo=commandInfo, target=user, role=role)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_removerole_name"),
        description=app_commands.locale_str("admin_removerole_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("admin_removerole_params_user_description"),
        role=app_commands.locale_str("admin_removerole_params_role_description"),
    )
    async def removerole(self, ctx, user: discord.Member, role: discord.Role):
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

        await removeroleCommand(commandInfo=commandInfo, target=user, role=role)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_createrole_name"),
        description=app_commands.locale_str("admin_createrole_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("admin_createrole_params_name_description"),
        color=app_commands.locale_str("admin_createrole_params_color_description"),
        display_icon=app_commands.locale_str(
            "admin_createrole_params_display_icon_description"
        ),
        hoist=app_commands.locale_str("admin_createrole_params_hoist_description"),
        mentionable=app_commands.locale_str(
            "admin_createrole_params_mentionable_description"
        ),
        reason=app_commands.locale_str("admin_createrole_params_reason_description"),
        display_emoji=app_commands.locale_str(
            "admin_createrole_params_display_emoji_description"
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
            "admin_ban_params_delete_message_days_description"
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
            setting=setting.value,
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
    async def say(self, ctx, channel: discord.TextChannel, *, message: str):
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

        if channel == None:
            channel = ctx.channel

        await createEmbedCommand(commandInfo=commandInfo, channel=channel, title=title)
        return

    @app_commands.command(
        name=app_commands.locale_str("admin_createemoji_name"),
        description=app_commands.locale_str("admin_createemoji_description"),
    )
    @app_commands.describe(
        name=app_commands.locale_str("admin_createemoji_params_name_description"),
        image_url=app_commands.locale_str(
            "admin_createemoji_params_imageUrl_description"
        ),
    )
    async def createemoji(self, ctx, name: str, image_url: str):
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
                commandInfo=commandInfo, name=name, image_url=image_url, roles=roles
            )

        role_select.callback = role_select_callback
        view.add_item(role_select)
        await ctx.followup.send(
            tanjunLocalizer.localize(
                ctx.locale, "commands.admin.createEmoji.roleSelect"
            ),
            view=view,
        )


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

        if channel == None:
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


    @commands.Cog.listener()
    async def on_ready(self):
        admincmds = administrationCommands(
            name="admin", description="Administriere den Server"
        )
        warncmds = WarnCommands(name="warn", description="Verwalte Warnungen")
        admincmds.add_command(warncmds)
        self.bot.tree.add_command(admincmds)

async def setup(bot):
    await bot.add_cog(adminCog(bot))
