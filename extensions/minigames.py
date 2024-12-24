import discord
from discord.ext import commands
from discord import app_commands
import utility
from utility import tanjunEmbed
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.minigames.counting.setcountingchannel import (
    setCountingChannel as setCountingChannelCommand,
)
from commands.minigames.counting.removecountingchannel import (
    removeCountingChannel as removeCountingChannelCommand,
)
from commands.minigames.counting.setcountingprogress import (
    setCountingProgress as setCountingProgressCommand,
)
from commands.minigames.countingChallenge.setcountingchannel import (
    setCountingChannel as setCountingChallengeChannelCommand,
)
from commands.minigames.countingChallenge.removecountingchannel import (
    removecountingchallengechannel as removeCountingChallengeChannelCommand,
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
from commands.minigames.wordchain.setwordchainchannel import (
    setwordchainchannel as setWordChainChannelCommand,
)
from commands.minigames.wordchain.removewordchainchannel import (
    removewordchainchannel as removeWordChainChannelCommand,
)

class CountingCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcountingch_name"),
        description=app_commands.locale_str("minigames_setcountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_setcountingch_params_channel_description"
        ),
    )
    async def setcountingchannel(self, ctx, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await setCountingChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removecountingch_name"),
        description=app_commands.locale_str("minigames_removecountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_removecountingch_params_channel_description"
        ),
    )
    async def removecountingchannel(self, ctx, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await removeCountingChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcprogress_name"),
        description=app_commands.locale_str("minigames_setcprogress_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_setcprogress_params_channel_description"
        ),
        progress=app_commands.locale_str(
            "minigames_setcprogress_params_progress_description"
        ),
    )
    async def setcountingprogress(
        self, ctx, channel: discord.TextChannel = None, progress: int = 0
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

        if not channel:
            channel = ctx.channel

        await setCountingProgressCommand(commandInfo, channel, progress)


class CountingChallengeCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcchallengech_name"),
        description=app_commands.locale_str("minigames_setcchallengech_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_setcchallengech_params_channel_description"
        ),
    )
    async def setcountingchallengechannel(
        self, ctx, channel: discord.TextChannel = None
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

        if not channel:
            channel = ctx.channel

        await setCountingChallengeChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_rcchallengech_name"),
        description=app_commands.locale_str("minigames_rcchallengech_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_rcchallengech_params_channel_description"
        ),
    )
    async def removecountingchallengechannel(
        self, ctx, channel: discord.TextChannel = None
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

        if not channel:
            channel = ctx.channel

        await removeCountingChallengeChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcchallengep_name"),
        description=app_commands.locale_str("minigames_setcchallengep_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_setcchallengep_params_channel_description"
        ),
        progress=app_commands.locale_str(
            "minigames_setcchallengep_params_progress_description"
        ),
    )
    async def setcountingchallengeprogress(
        self, ctx, channel: discord.TextChannel = None, progress: int = 0
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

        if not channel:
            channel = ctx.channel

        await setCountingChallengeProgressCommand(commandInfo, channel, progress)


class CountingModesCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setcmodesch_name"),
        description=app_commands.locale_str("minigames_setcmodesch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setcmodesch_params_channel_description"),
    )
    async def setcountingmodeschannel(self, ctx, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await setCountingModesChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removecmodesch_name"),
        description=app_commands.locale_str("minigames_removecmodesch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_removecmodesch_params_channel_description"
        ),
    )
    async def removecountingmodeschannel(
        self, ctx, channel: discord.TextChannel = None
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

        if not channel:
            channel = ctx.channel

        await removeCountingModesChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_setcmodesprogress_name"),
        description=app_commands.locale_str("minigames_setcmodesprogress_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_setcmodesprogress_params_channel_description"
        ),
        progress=app_commands.locale_str(
            "minigames_setcmodesprogress_params_progress_description"
        ),
    )
    async def setcountingmodesprogress(
        self, ctx, channel: discord.TextChannel = None, progress: int = 0
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

        if not channel:
            channel = ctx.channel

        await setCountingModesProgressCommand(commandInfo, channel, progress)


class WordChainCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("minigames_setwordcainch_name"),
        description=app_commands.locale_str("minigames_setwordcainch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str("minigames_setwordcainch_params_channel_description"),
    )
    async def setwordchainchannel(self, ctx, channel: discord.TextChannel = None):
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

        if not channel:
            channel = ctx.channel

        await setWordChainChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("minigames_removewordchch_name"),
        description=app_commands.locale_str("minigames_removewordchch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "minigames_removewordchch_params_channel_description"
        ),
    )
    async def removewordchainchannel(
        self, ctx, channel: discord.TextChannel = None
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

        if not channel:
            channel = ctx.channel

        await removeWordChainChannelCommand(commandInfo, channel)


class minigameCommands(discord.app_commands.Group): ...


class minigameCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        minigameCmds = minigameCommands(
            name="minigame", description="Minigame Commands"
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
        self.bot.tree.add_command(minigameCmds)


async def setup(bot):
    await bot.add_cog(minigameCog(bot))
