from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import utility
from commands.fun.funcommands import fun_command


class funCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("fun_hug_name"),
        description=app_commands.locale_str("fun_hug_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_hug_params_member_description"),
        message=app_commands.locale_str("fun_hug_params_message_description"),
    )
    async def hug(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "hug"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_kiss_name"),
        description=app_commands.locale_str("fun_kiss_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_kiss_params_member_description"),
        message=app_commands.locale_str("fun_kiss_params_message_description"),
    )
    async def kiss(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "kiss"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_boop_name"),
        description=app_commands.locale_str("fun_boop_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_boop_params_member_description"),
        message=app_commands.locale_str("fun_boop_params_message_description"),
    )
    async def boop(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "boop"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_wave_name"),
        description=app_commands.locale_str("fun_wave_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_wave_params_member_description"),
        message=app_commands.locale_str("fun_wave_params_message_description"),
    )
    async def wave(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "wave"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_slap_name"),
        description=app_commands.locale_str("fun_slap_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_slap_params_member_description"),
        message=app_commands.locale_str("fun_slap_params_message_description"),
    )
    async def slap(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "slap"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_laugh_name"),
        description=app_commands.locale_str("fun_laugh_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_laugh_params_member_description"),
        message=app_commands.locale_str("fun_laugh_params_message_description"),
    )
    async def laugh(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "laugh"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_tickle_name"),
        description=app_commands.locale_str("fun_tickle_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_tickle_params_member_description"),
        message=app_commands.locale_str("fun_tickle_params_message_description"),
    )
    async def tickle(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "tickle"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_pat_name"),
        description=app_commands.locale_str("fun_pat_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_pat_params_member_description"),
        message=app_commands.locale_str("fun_pat_params_message_description"),
    )
    async def pat(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "pat"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)

    @app_commands.command(
        name=app_commands.locale_str("fun_poke_name"),
        description=app_commands.locale_str("fun_poke_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("fun_poke_params_member_description"),
        message=app_commands.locale_str("fun_poke_params_message_description"),
    )
    async def poke(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        message: app_commands.Range[str, 0, 2000] = None,  # type: ignore[assignment]
    ) -> None:
        fun_type = "poke"
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
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

        await fun_command(commandInfo, fun_type, user, message)


class funCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        utilityCmds = funCommands(
            name=app_commands.locale_str("funcmd_name"), description=app_commands.locale_str("funcmd_description")
        )
        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(utilityCmds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(funCog(bot))
