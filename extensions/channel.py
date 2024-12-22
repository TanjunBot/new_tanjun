import discord
from discord.ext import commands
from discord import app_commands
import utility
from localizer import tanjunLocalizer

from commands.admin.channel.welcome import (
    setWelcomeChannel as setWelcomeChannelCommand,
    removeWelcomeChannel as removeWelcomeChannelCommand,
)
from commands.admin.channel.farewell import (
    setFarewellChannel as setFarewellChannelCommand,
    removeFarewellChannel as removeFarewellChannelCommand,
)
from commands.admin.channel.media import (
    addMediaChannel as addMediaChannelCommand,
    removeMediaChannel as removeMediaChannelCommand,
)


class WelcomeCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_ch_w_name"),
        description=app_commands.locale_str("channel_ch_w_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("channel_ch_w_params_channel_description"),
        message=app_commands.locale_str("channel_ch_w_params_message_description"),
        background=app_commands.locale_str("channel_ch_w_params_image_description"),
    )
    async def welcome(
        self,
        ctx,
        channel: discord.TextChannel = None,
        message: str = None,
        background: discord.Attachment = None,
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

        await setWelcomeChannelCommand(
            commandInfo=commandInfo,
            channel=channel,
            message=message,
            image_background=background,
        )
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_ch_w_remove_name"),
        description=app_commands.locale_str("channel_ch_w_remove_description"),
    )
    async def remove_welcome(self, ctx):
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

        await removeWelcomeChannelCommand(commandInfo=commandInfo)
        return


class FarewellCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_farewell_set_ch_name"),
        description=app_commands.locale_str("channel_farewell_set_ch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "channel_farewell_set_ch_params_channel_description"
        ),
        message=app_commands.locale_str(
            "channel_farewell_set_ch_params_message_description"
        ),
        background=app_commands.locale_str(
            "channel_farewell_set_ch_params_image_description"
        ),
    )
    async def set_farewell_channel(
        self,
        ctx,
        channel: discord.TextChannel = None,
        message: str = None,
        background: discord.Attachment = None,
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

        await setFarewellChannelCommand(commandInfo, channel, message, background)
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_farewell_remove_ch_name"),
        description=app_commands.locale_str("channel_farewell_remove_ch_description"),
    )
    async def remove_farewell_channel(self, ctx):
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

        await removeFarewellChannelCommand(commandInfo=commandInfo)
        return


class MediaCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("channel_channel_media_name"),
        description=app_commands.locale_str("channel_channel_media_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "channel_channel_media_params_channel_description"
        ),
    )
    async def media_add_cmd(self, ctx, channel: discord.TextChannel):
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

        await addMediaChannelCommand(commandInfo=commandInfo, channel=channel)
        return

    @app_commands.command(
        name=app_commands.locale_str("channel_channel_mediaremove_name"),
        description=app_commands.locale_str("channel_channel_mediaremove_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "channel_channel_mediaremove_params_channel_description"
        ),
    )
    async def media_remove_cmd(self, ctx, channel: discord.TextChannel):
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

        await removeMediaChannelCommand(commandInfo=commandInfo, channel=channel)
        return




class ChannelCommands(discord.app_commands.Group):
    def __init__(self):
        super().__init__(
            name=app_commands.locale_str("channel_name"),
            description=app_commands.locale_str("channel_description"),
        )


class ChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
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

        channel_commands.add_command(welcome_commands)
        channel_commands.add_command(farewell_commands)
        channel_commands.add_command(media_commands)

        self.bot.tree.add_command(channel_commands)


async def setup(bot):
    await bot.add_cog(ChannelCog(bot))
