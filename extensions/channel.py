from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.channel.dynamicslowmode import addDynamicslowmode as addDynamicslowmodeCommand
from commands.channel.dynamicslowmode import getDynamicslowmode_channels as getDynamicslowmodeChannelsCommand
from commands.channel.dynamicslowmode import removeDynamicslowmode as removeDynamicslowmodeCommand
from commands.channel.farewell import removeFarewellChannel as removeFarewellChannelCommand
from commands.channel.farewell import setFarewellChannel as setFarewellChannelCommand
from commands.channel.media import addMediaChannel as addMediaChannelCommand
from commands.channel.media import removeMediaChannel as removeMediaChannelCommand
from commands.channel.welcome import removeWelcomeChannel as removeWelcomeChannelCommand
from commands.channel.welcome import setWelcomeChannel as setWelcomeChannelCommand

class WelcomeCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.channel.w.name.discord_key, description=locale.channel.w.description.discord_key)
    @app_commands.describe(channel=locale.channel.w.params.channel.description.discord_key, message=locale.channel.w.params.message.description.discord_key, background=locale.channel.w.params.image.description.discord_key)
    async def welcome(self, interaction: discord.Interaction, channel: discord.TextChannel=None, message: app_commands.Range[str, 0, 1024]=None, background: discord.Attachment=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await setWelcomeChannelCommand(command_info=command_info, channel=channel, message=message, image_background=background)
        return

    @app_commands.command(name=locale.channel.w.remove.name.discord_key, description=locale.channel.w.remove.description.discord_key)
    async def remove_welcome(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeWelcomeChannelCommand(command_info=command_info)
        return

class FarewellCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.channel.farewell.set.ch.name.discord_key, description=locale.channel.farewell.set.ch.description.discord_key)
    @app_commands.describe(channel=locale.channel.farewell.set.ch.params.channel.description.discord_key, message=locale.channel.farewell.set.ch.params.message.description.discord_key, background=locale.channel.farewell.set.ch.params.image.description.discord_key)
    async def set_farewell_channel(self, interaction: discord.Interaction, channel: discord.TextChannel=None, message: app_commands.Range[str, 0, 1024]=None, background: discord.Attachment=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await setFarewellChannelCommand(command_info, channel, message, background)
        return

    @app_commands.command(name=locale.channel.farewell.remove.ch.name.discord_key, description=locale.channel.farewell.remove.ch.description.discord_key)
    async def remove_farewell_channel(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeFarewellChannelCommand(command_info=command_info)
        return

class MediaCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.channel.media.name.discord_key, description=locale.channel.media.description.discord_key)
    @app_commands.describe(channel=locale.channel.media.params.channel.description.discord_key)
    async def media_add_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await addMediaChannelCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.channel.mediaremove.name.discord_key, description=locale.channel.mediaremove.description.discord_key)
    @app_commands.describe(channel=locale.channel.mediaremove.params.channel.description.discord_key)
    async def media_remove_cmd(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeMediaChannelCommand(command_info=command_info, channel=channel)
        return

class DynamicslowmodeCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.channel.ds.add.name.discord_key, description=locale.channel.ds.add.description.discord_key)
    @app_commands.describe(channel=locale.channel.ds.add.params.channel.description.discord_key, messages=locale.channel.ds.add.params.messages.description.discord_key, per=locale.channel.ds.add.params.per.description.discord_key, resetafter=locale.channel.ds.add.params.resetafter.description.discord_key)
    async def add_dynamicslowmode(self, interaction: discord.Interaction, channel: discord.TextChannel, messages: app_commands.Range[int, 1, 2147483647], per: app_commands.Range[int, 1, 2147483647], resetafter: app_commands.Range[int, 1, 2147483647]=60) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await addDynamicslowmodeCommand(command_info=command_info, channel=channel, messages=messages, per=per, resetafter=resetafter)
        return

    @app_commands.command(name=locale.channel.ds.remove.name.discord_key, description=locale.channel.ds.remove.description.discord_key)
    @app_commands.describe(channel=locale.channel.ds.remove.params.channel.description.discord_key)
    async def remove_dynamicslowmode(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await removeDynamicslowmodeCommand(command_info=command_info, channel=channel)
        return

    @app_commands.command(name=locale.channel.ds.get.name.discord_key, description=locale.channel.ds.get.description.discord_key)
    async def get_dynamicslowmode_channels(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await getDynamicslowmodeChannelsCommand(command_info=command_info)
        return

class ChannelCommands(discord.app_commands.Group):

    def __init__(self) -> None:
        super().__init__(name=locale.channel.name.discord_key, description=locale.channel.description.discord_key)

class ChannelCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        channel_commands = ChannelCommands()
        welcome_commands = WelcomeCommands(name=locale.channel.welcome.name.discord_key, description=locale.channel.welcome.description.discord_key)
        farewell_commands = FarewellCommands(name=locale.channel.farewell.name.discord_key, description=locale.channel.farewell.description.discord_key)
        media_commands = MediaCommands(name=locale.channel.media.name.discord_key, description=locale.channel.media.description.discord_key)
        dynamicslowmode_commands = DynamicslowmodeCommands(name=locale.channel.ds.name.discord_key, description=locale.channel.ds.description.discord_key)
        channel_commands.add_command(welcome_commands)
        channel_commands.add_command(farewell_commands)
        channel_commands.add_command(media_commands)
        channel_commands.add_command(dynamicslowmode_commands)
        if self.bot.tree:
            self.bot.tree.add_command(channel_commands)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ChannelCog(bot))