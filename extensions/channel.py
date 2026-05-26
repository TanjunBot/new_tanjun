# Unused imports:
# from localizer import tanjunLocalizer
from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import utility
from commands.channel.dynamicslowmode import (
    addDynamicslowmode as addDynamicslowmodeCommand,
)
from commands.channel.dynamicslowmode import (
    getDynamicslowmodeChannels as getDynamicslowmodeChannelsCommand,
)
from commands.channel.dynamicslowmode import (
    removeDynamicslowmode as removeDynamicslowmodeCommand,
)
from commands.channel.farewell import (
    removeFarewellChannel as removeFarewellChannelCommand,
)
from commands.channel.farewell import (
    setFarewellChannel as setFarewellChannelCommand,
)
from commands.channel.media import (
    addMediaChannel as addMediaChannelCommand,
)
from commands.channel.media import (
    removeMediaChannel as removeMediaChannelCommand,
)
from commands.channel.welcome import (
    removeWelcomeChannel as removeWelcomeChannelCommand,
)
from commands.channel.welcome import (
    setWelcomeChannel as setWelcomeChannelCommand,
)


class WelcomeCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_w_name"),
        description=app_commands.locale_str("channel_w_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_w_params_channel_description"),
        message=app_commands.locale_str("channel_w_params_message_description"),
        background=app_commands.locale_str("channel_w_params_image_description"),
    )
    async def welcome(  # type: ignore[no-untyped-def]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        message: app_commands.Range[str, 0, 1024] = None,  # type: ignore[assignment]
        background: discord.Attachment = None,  # type: ignore[assignment]
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await setWelcomeChannelCommand(
            commandInfo=commandInfo,
            channel=channel,
            message=message,
            image_background=background,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_w_remove_name"),
        description=app_commands.locale_str("channel_w_remove_description"),
    )
    async def remove_welcome(self, interaction: discord.Interaction) -> None:
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

        await removeWelcomeChannelCommand(commandInfo=commandInfo)  # type: ignore[call-arg]
        return


class FarewellCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_farewell_set_ch_name"),
        description=app_commands.locale_str("channel_farewell_set_ch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_farewell_set_ch_params_channel_description"),
        message=app_commands.locale_str("channel_farewell_set_ch_params_message_description"),
        background=app_commands.locale_str("channel_farewell_set_ch_params_image_description"),
    )
    async def set_farewell_channel(  # type: ignore[no-untyped-def]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        message: app_commands.Range[str, 0, 1024] = None,  # type: ignore[assignment]
        background: discord.Attachment = None,  # type: ignore[assignment]
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await setFarewellChannelCommand(commandInfo, channel, message, background)
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_farewell_remove_ch_name"),
        description=app_commands.locale_str("channel_farewell_remove_ch_description"),
    )
    async def remove_farewell_channel(self, interaction: discord.Interaction) -> None:
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

        await removeFarewellChannelCommand(commandInfo=commandInfo)  # type: ignore[call-arg]
        return


class MediaCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_media_name"),
        description=app_commands.locale_str("channel_media_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_media_params_channel_description"),
    )
    async def media_add_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
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

        await addMediaChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_mediaremove_name"),
        description=app_commands.locale_str("channel_mediaremove_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_mediaremove_params_channel_description"),
    )
    async def media_remove_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
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

        await removeMediaChannelCommand(commandInfo=commandInfo, channel=channel)
        return


class DynamicslowmodeCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_ds_add_name"),
        description=app_commands.locale_str("channel_ds_add_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_ds_add_params_channel_description"),
        messages=app_commands.locale_str("channel_ds_add_params_messages_description"),
        per=app_commands.locale_str("channel_ds_add_params_per_description"),
        resetafter=app_commands.locale_str("channel_ds_add_params_resetafter_description"),
    )
    async def add_dynamicslowmode(  # type: ignore[no-untyped-def]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        messages: app_commands.Range[int, 1, 2147483647],
        per: app_commands.Range[int, 1, 2147483647],
        resetafter: app_commands.Range[int, 1, 2147483647] = 60,
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        await addDynamicslowmodeCommand(
            commandInfo=commandInfo,
            channel=channel,
            messages=messages,
            per=per,
            resetafter=resetafter,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_ds_remove_name"),
        description=app_commands.locale_str("channel_ds_remove_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_ds_remove_params_channel_description"),
    )
    async def remove_dynamicslowmode(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
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

        await removeDynamicslowmodeCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_ds_get_name"),
        description=app_commands.locale_str("channel_ds_get_description"),
    )
    async def get_dynamicslowmode_channels(self, interaction: discord.Interaction) -> None:
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

        await getDynamicslowmodeChannelsCommand(commandInfo=commandInfo)
        return


class ChannelCommands(discord.app_commands.Group):
    def __init__(self) -> None:
        super().__init__(  # type: ignore[misc]
            name=app_commands.locale_str("channel_name"),
            description=app_commands.locale_str("channel_description"),
        )


class ChannelCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        channel_commands = ChannelCommands()

        welcome_commands = WelcomeCommands(
            name=app_commands.locale_str("channel_welcome_name"),
            description=app_commands.locale_str("channel_welcome_description"),
        )
        farewell_commands = FarewellCommands(
            name=app_commands.locale_str("channel_farewell_name"),
            description=app_commands.locale_str("channel_farewell_description"),
        )
        media_commands = MediaCommands(
            name=app_commands.locale_str("channel_media_name"),
            description=app_commands.locale_str("channel_media_description"),
        )
        dynamicslowmode_commands = DynamicslowmodeCommands(
            name=app_commands.locale_str("channel_ds_name"),
            description=app_commands.locale_str("channel_ds_description"),
        )

        channel_commands.add_command(welcome_commands)
        channel_commands.add_command(farewell_commands)
        channel_commands.add_command(media_commands)
        channel_commands.add_command(dynamicslowmode_commands)

        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(channel_commands)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelCog(bot))
