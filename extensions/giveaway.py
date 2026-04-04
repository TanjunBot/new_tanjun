from typing import cast

import discord  # type: ignore[import-not-found]
from discord import app_commands
from discord.ext import commands  # type: ignore[import-not-found]

import utility
from commands.giveaway.add_blacklist_role import add_blacklist_role
from commands.giveaway.add_blacklist_user import add_blacklist_user
from commands.giveaway.edit_giveaway import edit_giveaway
from commands.giveaway.end_giveaway import end_giveaway
from commands.giveaway.list_blacklist import list_blacklist
from commands.giveaway.remove_blacklist_role import remove_blacklist_role
from commands.giveaway.remove_blacklist_user import remove_blacklist_user
from commands.giveaway.reroll_giveaway import reroll_giveaway
from commands.giveaway.start import start_giveaway


class BlacklistCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_bl_add_role_name"),
        description=app_commands.locale_str("giveaway_bl_add_role_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("giveaway_bl_add_role_role_description"),
    )
    async def add_role(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        role: discord.Role,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await add_blacklist_role(
            commandInfo=commandInfo,
            role=role,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_bl_remove_role_name"),
        description=app_commands.locale_str("giveaway_bl_remove_role_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        role=app_commands.locale_str("giveaway_bl_remove_role_role_description"),
    )
    async def remove_role(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        role: discord.Role,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await remove_blacklist_role(
            commandInfo=commandInfo,
            role=role,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_bl_add_user_name"),
        description=app_commands.locale_str("giveaway_bl_add_user_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("giveaway_bl_add_user_user_description"),
    )
    async def add_user(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        user: discord.User,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await add_blacklist_user(
            commandInfo=commandInfo,
            user=user,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_bl_remove_user_name"),
        description=app_commands.locale_str("giveaway_bl_remove_user_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        user=app_commands.locale_str("giveaway_bl_remove_user_user_description"),
    )
    async def remove_user(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        user: discord.User,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await remove_blacklist_user(
            commandInfo=commandInfo,
            user=user,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_bl_list_name"),
        description=app_commands.locale_str("giveaway_bl_list_description"),
    )
    async def list(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await list_blacklist(
            commandInfo=commandInfo,
        )


class GiveawayCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_start_name"),
        description=app_commands.locale_str("giveaway_start_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        title=app_commands.locale_str("giveaway_start_params_title_description"),
        channel=app_commands.locale_str("giveaway_start_params_channel_description"),
    )
    async def start(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        title: app_commands.Range[str, 0, 128],
        channel: discord.TextChannel = None,
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
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

        await ctx.response.defer()
        await start_giveaway(  # type: ignore[no-untyped-call]
            commandInfo=commandInfo,
            title=title,
            target_channel=channel,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_end_name"),
        description=app_commands.locale_str("giveaway_end_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        giveawayid=app_commands.locale_str("giveaway_end_params_giveawayid_description"),
    )
    async def end(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await end_giveaway(
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_reroll_name"),
        description=app_commands.locale_str("giveaway_reroll_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        giveawayid=app_commands.locale_str("giveaway_reroll_params_giveawayid_description"),
    )
    async def reroll(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await reroll_giveaway(
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("giveaway_edit_name"),
        description=app_commands.locale_str("giveaway_edit_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        giveawayid=app_commands.locale_str("giveaway_edit_params_giveawayid_description"),
    )
    async def edit(  # type: ignore[misc,no-any-unimported]
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        commandInfo = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),  # type: ignore[no-any-unimported]
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await edit_giveaway(  # type: ignore[no-untyped-call]
            commandInfo=commandInfo,
            giveawayId=giveawayid,
        )


class GiveawayCog(commands.Cog):  # type: ignore[misc,no-any-unimported]
    def __init__(self, bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
        self.bot = bot

    @commands.Cog.listener()  # type: ignore[untyped-decorator]
    async def on_ready(self) -> None:  # type: ignore[misc]
        giveaway_commands = GiveawayCommands(
            name=app_commands.locale_str("giveaway_name"), description=app_commands.locale_str("giveaway_description")
        )
        blacklistCmds = BlacklistCommands(
            name=app_commands.locale_str("giveaway_blacklist_name"),
            description=app_commands.locale_str("giveaway_blacklist_description"),
        )
        giveaway_commands.add_command(blacklistCmds)
        if self.bot.tree:
            self.bot.tree.add_command(giveaway_commands)


async def setup(bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
    await bot.add_cog(GiveawayCog(bot))
