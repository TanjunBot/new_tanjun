from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

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


class BlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_add_role_name"),
        description=app_commands.locale_str("giveaway_bl_add_role_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("giveaway_bl_add_role_role_description"),
    )
    async def add_role(
        self,
        ctx: discord.Interaction,
        role: discord.Role,
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await add_blacklist_role(
            command_info=command_info,
            role=role,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_remove_role_name"),
        description=app_commands.locale_str("giveaway_bl_remove_role_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("giveaway_bl_remove_role_role_description"),
    )
    async def remove_role(
        self,
        ctx: discord.Interaction,
        role: discord.Role,
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await remove_blacklist_role(
            command_info=command_info,
            role=role,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_add_user_name"),
        description=app_commands.locale_str("giveaway_bl_add_user_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("giveaway_bl_add_user_user_description"),
    )
    async def add_user(
        self,
        ctx: discord.Interaction,
        user: discord.User,
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await add_blacklist_user(
            command_info=command_info,
            user=user,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_remove_user_name"),
        description=app_commands.locale_str("giveaway_bl_remove_user_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("giveaway_bl_remove_user_user_description"),
    )
    async def remove_user(
        self,
        ctx: discord.Interaction,
        user: discord.User,
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await remove_blacklist_user(
            command_info=command_info,
            user=user,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_bl_list_name"),
        description=app_commands.locale_str("giveaway_bl_list_description"),
    )
    async def list(
        self,
        ctx: discord.Interaction,
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await list_blacklist(
            command_info=command_info,
        )


class GiveawayCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("giveaway_start_name"),
        description=app_commands.locale_str("giveaway_start_description"),
    )
    @app_commands.describe(
        title=app_commands.locale_str("giveaway_start_params_title_description"),
        channel=app_commands.locale_str("giveaway_start_params_channel_description"),
    )
    async def start(
        self,
        ctx: discord.Interaction,
        title: app_commands.Range[str, 0, 128],
        channel: discord.TextChannel = None,  # type: ignore[assignment]
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        if not channel:  # type: ignore[truthy-bool]
            channel = ctx.channel  # type: ignore[assignment]

        await ctx.response.defer()
        await start_giveaway(  # type: ignore[no-untyped-call]
            command_info=command_info,
            title=title,
            target_channel=channel,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_end_name"),
        description=app_commands.locale_str("giveaway_end_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_end_params_giveawayid_description"),
    )
    async def end(
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await end_giveaway(
            command_info=command_info,
            giveaway_id=giveawayid,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_reroll_name"),
        description=app_commands.locale_str("giveaway_reroll_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_reroll_params_giveawayid_description"),
    )
    async def reroll(
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await reroll_giveaway(
            command_info=command_info,
            giveaway_id=giveawayid,
        )

    @app_commands.command(
        name=app_commands.locale_str("giveaway_edit_name"),
        description=app_commands.locale_str("giveaway_edit_description"),
    )
    @app_commands.describe(
        giveawayid=app_commands.locale_str("giveaway_edit_params_giveawayid_description"),
    )
    async def edit(
        self,
        ctx: discord.Interaction,
        giveawayid: app_commands.Range[int, 1, 4294967295],
    ) -> None:
        command_info = utility.CommandInfo(
            user=ctx.user,
            channel=cast(discord.abc.GuildChannel, ctx.channel),
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,  # type: ignore[arg-type]
            message=ctx.message,
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await ctx.response.defer()
        await edit_giveaway(  # type: ignore[no-untyped-call]
            command_info=command_info,
            giveaway_id=giveawayid,
        )


class GiveawayCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        giveaway_commands = GiveawayCommands(
            name=app_commands.locale_str("giveaway_name"), description=app_commands.locale_str("giveaway_description")
        )
        blacklist_cmds = BlacklistCommands(
            name=app_commands.locale_str("giveaway_blacklist_name"),
            description=app_commands.locale_str("giveaway_blacklist_description"),
        )
        giveaway_commands.add_command(blacklist_cmds)
        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(giveaway_commands)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GiveawayCog(bot))
