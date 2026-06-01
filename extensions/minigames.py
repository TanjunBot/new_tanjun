from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.minigames.counting.removecountingchannel import removeCountingChannel as removeCountingChannelCommand
from commands.minigames.counting.setcountingchannel import setCountingChannel as setCountingChannelCommand
from commands.minigames.counting.setcountingprogress import setCountingProgress as setCountingProgressCommand
from commands.minigames.counting_challenge.removecountingchannel import removecountingchallengechannel as removeCountingChallengeChannelCommand
from commands.minigames.counting_challenge.setcountingchannel import setCountingChannel as setCountingChallengeChannelCommand
from commands.minigames.counting_challenge.setcountingprogress import setCountingProgress as setCountingChallengeProgressCommand
from commands.minigames.counting_modes.removecountingchannel import removecountingmodeschannel as removeCountingModesChannelCommand
from commands.minigames.counting_modes.setcountingchannel import setCountingChannel as setCountingModesChannelCommand
from commands.minigames.counting_modes.setcountingprogress import setCountingProgress as setCountingModesProgressCommand
from commands.minigames.wordchain.removewordchainchannel import removewordchainchannel as removeWordChainChannelCommand
from commands.minigames.wordchain.setwordchainchannel import setwordchainchannel as setWordChainChannelCommand

class CountingCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.minigames.setcountingch.name.discord_key, description=locale.minigames.setcountingch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcountingch.params.channel.description.discord_key)
    async def setcountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.removecountingch.name.discord_key, description=locale.minigames.removecountingch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.removecountingch.params.channel.description.discord_key)
    async def removecountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await removeCountingChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.setcprogress.name.discord_key, description=locale.minigames.setcprogress.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcprogress.params.channel.description.discord_key, progress=locale.minigames.setcprogress.params.progress.description.discord_key)
    async def setcountingprogress(self, interaction: discord.Interaction, channel: discord.TextChannel=None, progress: app_commands.Range[int, 1, 100000]=0) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingProgressCommand(command_info, channel, progress)

class CountingChallengeCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.minigames.setcchallengech.name.discord_key, description=locale.minigames.setcchallengech.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcchallengech.params.channel.description.discord_key)
    async def setcountingchallengechannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingChallengeChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.rcchallengech.name.discord_key, description=locale.minigames.rcchallengech.description.discord_key)
    @app_commands.describe(channel=locale.minigames.rcchallengech.params.channel.description.discord_key)
    async def removecountingchallengechannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await removeCountingChallengeChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.setcchallengep.name.discord_key, description=locale.minigames.setcchallengep.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcchallengep.params.channel.description.discord_key, progress=locale.minigames.setcchallengep.params.progress.description.discord_key)
    async def setcountingchallengeprogress(self, interaction: discord.Interaction, channel: discord.TextChannel=None, progress: app_commands.Range[int, 1, 100000]=0) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingChallengeProgressCommand(command_info, channel, progress)

class CountingModesCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.minigames.setcmodesch.name.discord_key, description=locale.minigames.setcmodesch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcmodesch.params.channel.description.discord_key)
    async def setcountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingModesChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.removecmodesch.name.discord_key, description=locale.minigames.removecmodesch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.removecmodesch.params.channel.description.discord_key)
    async def removecountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await removeCountingModesChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.setcmodesprogress.name.discord_key, description=locale.minigames.setcmodesprogress.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setcmodesprogress.params.channel.description.discord_key, progress=locale.minigames.setcmodesprogress.params.progress.description.discord_key)
    async def setcountingmodesprogress(self, interaction: discord.Interaction, channel: discord.TextChannel=None, progress: app_commands.Range[int, 1, 100000]=0) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setCountingModesProgressCommand(command_info, channel, progress)

class WordChainCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.minigames.setwordcainch.name.discord_key, description=locale.minigames.setwordcainch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.setwordcainch.params.channel.description.discord_key)
    async def setwordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await setWordChainChannelCommand(command_info, channel)

    @app_commands.command(name=locale.minigames.removewordchch.name.discord_key, description=locale.minigames.removewordchch.description.discord_key)
    @app_commands.describe(channel=locale.minigames.removewordchch.params.channel.description.discord_key)
    async def removewordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel=None) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)
        await removeWordChainChannelCommand(command_info, channel)

class MinigameCommands(discord.app_commands.Group):
    pass

class MinigameCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        minigame_cmds = MinigameCommands(name=locale.minigame.name.discord_key, description=locale.minigame.description.discord_key)
        counting_cmds = CountingCommands(name=locale.minigames.countingcmds.name.discord_key, description=locale.minigames.countingcmds.description.discord_key)
        counting_challenge_cmds = CountingChallengeCommands(name=locale.minigames.cchcmds.name.discord_key, description=locale.minigames.cchcmds.description.discord_key)
        counting_modes_cmds = CountingModesCommands(name=locale.minigames.cmodescmds.name.discord_key, description=locale.minigames.cmodescmds.description.discord_key)
        word_chain_cmds = WordChainCommands(name=locale.minigames.wordchaincmds.name.discord_key, description=locale.minigames.wordchaincmds.description.discord_key)
        minigame_cmds.add_command(counting_cmds)
        minigame_cmds.add_command(counting_challenge_cmds)
        minigame_cmds.add_command(counting_modes_cmds)
        minigame_cmds.add_command(word_chain_cmds)
        if self.bot.tree:
            self.bot.tree.add_command(minigame_cmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MinigameCog(bot))