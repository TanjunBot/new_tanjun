from typing import cast

import discord  # type: ignore[import-not-found]
from discord import app_commands
from discord.ext import commands  # type: ignore[import-not-found]

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


class CountingCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcountingch_name"),
        description=app_commands.locale_str("minigames_setcountingch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcountingch_params_channel_description"),
    )
    async def setcountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_removecountingch_name"),
        description=app_commands.locale_str("minigames_removecountingch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_removecountingch_params_channel_description"),
    )
    async def removecountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await removeCountingChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcprogress_name"),
        description=app_commands.locale_str("minigames_setcprogress_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcprogress_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcprogress_params_progress_description"),
    )
    async def setcountingprogress(  # type: ignore[misc,no-any-unimported]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingProgressCommand(commandInfo, channel, progress)


class CountingChallengeCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcchallengech_name"),
        description=app_commands.locale_str("minigames_setcchallengech_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcchallengech_params_channel_description"),
    )
    async def setcountingchallengechannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingChallengeChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_rcchallengech_name"),
        description=app_commands.locale_str("minigames_rcchallengech_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_rcchallengech_params_channel_description"),
    )
    async def removecountingchallengechannel(  # type: ignore[misc,no-any-unimported]
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await removeCountingChallengeChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcchallengep_name"),
        description=app_commands.locale_str("minigames_setcchallengep_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcchallengep_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcchallengep_params_progress_description"),
    )
    async def setcountingchallengeprogress(  # type: ignore[misc,no-any-unimported]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingChallengeProgressCommand(commandInfo, channel, progress)


class CountingModesCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcmodesch_name"),
        description=app_commands.locale_str("minigames_setcmodesch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcmodesch_params_channel_description"),
    )
    async def setcountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingModesChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_removecmodesch_name"),
        description=app_commands.locale_str("minigames_removecmodesch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_removecmodesch_params_channel_description"),
    )
    async def removecountingmodeschannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await removeCountingModesChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setcmodesprogress_name"),
        description=app_commands.locale_str("minigames_setcmodesprogress_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setcmodesprogress_params_channel_description"),
        progress=app_commands.locale_str("minigames_setcmodesprogress_params_progress_description"),
    )
    async def setcountingmodesprogress(  # type: ignore[misc,no-any-unimported]
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        progress: app_commands.Range[int, 1, 100000] = 0,
    ) -> None:
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setCountingModesProgressCommand(commandInfo, channel, progress)


class WordChainCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_setwordcainch_name"),
        description=app_commands.locale_str("minigames_setwordcainch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_setwordcainch_params_channel_description"),
    )
    async def setwordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await setWordChainChannelCommand(commandInfo, channel)

    @app_commands.command(  # type: ignore[untyped-decorator]
        name=app_commands.locale_str("minigames_removewordchch_name"),
        description=app_commands.locale_str("minigames_removewordchch_description"),
    )
    @app_commands.describe(  # type: ignore[untyped-decorator]
        channel=app_commands.locale_str("minigames_removewordchch_params_channel_description"),
    )
    async def removewordchainchannel(self, interaction: discord.Interaction, channel: discord.TextChannel = None) -> None:  # type: ignore[misc,no-any-unimported]
        await interaction.response.defer()
        commandInfo = utility.CommandInfo(
            user=interaction.user,
            channel=cast(discord.abc.GuildChannel, interaction.channel),  # type: ignore[no-any-unimported]
            guild=interaction.guild,
            command=interaction.command,
            locale=interaction.locale,
            message=interaction.message,
            permissions=interaction.permissions,
            reply=interaction.followup.send,
            client=interaction.client,
        )

        if not channel:
            channel = cast(discord.TextChannel, interaction.channel)  # type: ignore[no-any-unimported]

        await removeWordChainChannelCommand(commandInfo, channel)


class minigameCommands(discord.app_commands.Group):  # type: ignore[misc,no-any-unimported]
    pass


class minigameCog(commands.Cog):  # type: ignore[misc,no-any-unimported]
    def __init__(self, bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
        self.bot = bot

    @commands.Cog.listener()  # type: ignore[untyped-decorator]
    async def on_ready(self) -> None:  # type: ignore[misc]
        minigameCmds = minigameCommands(
            name=app_commands.locale_str("minigame_name"),
            description=app_commands.locale_str("minigame_description"),
        )
        countingCmds = CountingCommands(
            name=app_commands.locale_str("minigames_countingcmds_name"),
            description=app_commands.locale_str("minigames_countingcmds_description"),
        )
        countingChallengeCmds = CountingChallengeCommands(
            name=app_commands.locale_str("minigames_cchcmds_name"),
            description=app_commands.locale_str("minigames_cchcmds_description"),
        )
        countingModesCmds = CountingModesCommands(
            name=app_commands.locale_str("minigames_cmodescmds_name"),
            description=app_commands.locale_str("minigames_cmodescmds_description"),
        )
        wordChainCmds = WordChainCommands(
            name=app_commands.locale_str("minigames_wordchaincmds_name"),
            description=app_commands.locale_str("minigames_wordchaincmds_description"),
        )
        minigameCmds.add_command(countingCmds)
        minigameCmds.add_command(countingChallengeCmds)
        minigameCmds.add_command(countingModesCmds)
        minigameCmds.add_command(wordChainCmds)
        if self.bot.tree:
            self.bot.tree.add_command(minigameCmds)


async def setup(bot: commands.Bot) -> None:  # type: ignore[no-any-unimported]
    await bot.add_cog(minigameCog(bot))
