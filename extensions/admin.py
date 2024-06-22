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
        role=app_commands.locale_str("admin_deleterole_params_role_description")
    )
    async def deleterole(self, ctx, role: discord.Role):
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

        await deleteroleCommand(commandInfo=commandInfo, role=role)
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

        await removeTimeoutCommand(commandInfo=commandInfo, member=member, reason=reason)
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

        await removeTimeoutCommand(commandInfo=commandInfo, member=member, reason=reason)
        return


    @commands.Cog.listener()
    async def on_ready(self):
        admincmds = administrationCommands(
            name="admin", description="Administriere den Server"
        )
        self.bot.tree.add_command(admincmds)


async def setup(bot):
    await bot.add_cog(adminCog(bot))
