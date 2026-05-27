from typing import cast

import discord
from discord import app_commands
from discord.ext import commands

import utility
from commands.minigames.counting.removecountingchannel import (
    removeCountingChannel as removeCountingChannelCommand,
)
from commands.minigames.counting.setcountingchannel import (
    setCountingChannel as setCountingChannelCommand,
)
from commands.minigames.counting.setcountingprogress import (
    setCountingProgress as setCountingProgressCommand,
)
from commands.minigames.countingChallenge.removecountingchannel import (
    removecountingchallengechannel as removeCountingChallengeChannelCommand,
)
from commands.minigames.countingChallenge.setcountingchannel import (
    setCountingChannel as setCountingChallengeChannelCommand,
)
from commands.minigames.countingChallenge.setcountingprogress import (
    setCountingProgress as setCountingChallengeProgressCommand,
)
from commands.minigames.countingModes.removecountingchannel import (
    removecountingmodeschannel as removeCountingModesChannelCommand,
)
from commands.minigames.countingModes.setcountingchannel import (
    setCountingChannel as setCountingModesChannelCommand,
)
from commands.minigames.countingModes.setcountingprogress import (
    setCountingProgress as setCountingModesProgressCommand,
)
from commands.minigames.wordchain.removewordchainchannel import (
    removewordchainchannel as removeWordChainChannelCommand,
)
from commands.minigames.wordchain.setwordchainchannel import (
    setwordchainchannel as setWordChainChannelCommand,
)


class CountingCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcountingch_name"),
        description=app_commands.locale_str("minigames_setcountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcountingch_params_channel_description"),
    )
    async def setcountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removecountingch_name"),
        description=app_commands.locale_str("minigames_removecountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_removecountingch_params_channel_description"),
    )
    async def removecountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await removeCountingChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcprogress_name"),
        description=app_commands.locale_str("minigames_setcprogress_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcprogress_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcprogress_params_progress_description"),
    )
    async def setcountingprogress(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingProgressCommand(command_info, channel, progress)


class CountingChallengeCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcchallengech_name"),
        description=app_commands.locale_str("minigames_setcchallengech_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcchallengech_params_channel_description"),
    )
    async def setcountingchallengechannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingChallengeChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_rcchallengech_name"),
        description=app_commands.locale_str("minigames_rcchallengech_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_rcchallengech_params_channel_description"),
    )
    async def removecountingchallengechannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
    ) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await removeCountingChallengeChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcchallengep_name"),
        description=app_commands.locale_str("minigames_setcchallengep_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcchallengep_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcchallengep_params_progress_description"),
    )
    async def setcountingchallengeprogress(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingChallengeProgressCommand(command_info, channel, progress)


class CountingModesCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcmodesch_name"),
        description=app_commands.locale_str("minigames_setcmodesch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcmodesch_params_channel_description"),
    )
    async def setcountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingModesChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removecmodesch_name"),
        description=app_commands.locale_str("minigames_removecmodesch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_removecmodesch_params_channel_description"),
    )
    async def removecountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await removeCountingModesChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcmodesprogress_name"),
        description=app_commands.locale_str("minigames_setcmodesprogress_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcmodesprogress_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcmodesprogress_params_progress_description"),
    )
    async def setcountingmodesprogress(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,  # type: ignore[assignment]
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setCountingModesProgressCommand(command_info, channel, progress)


class WordChainCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setwordcainch_name"),
        description=app_commands.locale_str("minigames_setwordcainch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setwordcainch_params_channel_description"),
    )
    async def setwordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await setWordChainChannelCommand(command_info, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removewordchch_name"),
        description=app_commands.locale_str("minigames_removewordchch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_removewordchch_params_channel_description"),
    )
    async def removewordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[assignment]
        await interaction.response.defer()
        command_info = utility.CommandInfo(
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

        if not channel:  # type: ignore[truthy-bool]
            channel = cast(discord.TextChannel, interaction.channel)

        await removeWordChainChannelCommand(command_info, channel)


class MinigameCommands(discord.app_commands.Group):
    pass


class MinigameCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        minigame_cmds = MinigameCommands(
            name=app_commands.locale_str("minigame_name"),
            description=app_commands.locale_str("minigame_description"),
        )
        counting_cmds = CountingCommands(
            name=app_commands.locale_str("minigames_countingcmds_name"),
            description=app_commands.locale_str("minigames_countingcmds_description"),
        )
        counting_challenge_cmds = CountingChallengeCommands(
            name=app_commands.locale_str("minigames_cchcmds_name"),
            description=app_commands.locale_str("minigames_cchcmds_description"),
        )
        counting_modes_cmds = CountingModesCommands(
            name=app_commands.locale_str("minigames_cmodescmds_name"),
            description=app_commands.locale_str("minigames_cmodescmds_description"),
        )
        word_chain_cmds = WordChainCommands(
            name=app_commands.locale_str("minigames_wordchaincmds_name"),
            description=app_commands.locale_str("minigames_wordchaincmds_description"),
        )
        minigame_cmds.add_command(counting_cmds)
        minigame_cmds.add_command(counting_challenge_cmds)
        minigame_cmds.add_command(counting_modes_cmds)
        minigame_cmds.add_command(word_chain_cmds)
        if self.bot.tree:  # type: ignore[truthy-bool]
            self.bot.tree.add_command(minigame_cmds)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(MinigameCog(bot))
