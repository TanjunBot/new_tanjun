import discord
from discord.ext import commands
from discord import app_commands
import utility
from utility import tanjunEmbed
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.minigames.setcountingchannel import setCountingChannel as setCountingChannelCommand

from commands.minigames.removecountingchannel import removeCountingChannel as removeCountingChannelCommand



class CountingCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("games_setcountingch_name"),
        description=app_commands.locale_str("games_setcountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "games_setcountingch_params_channel_description"
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

        setCountingChannelCommand(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("games_removecountingch_name"),
        description=app_commands.locale_str("games_removecountingch_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "games_removecountingch_params_channel_description"
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

        removeCountingChannelCommand(commandInfo, channel)


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
            name=app_commands.locale_str("minigame_countingcmds_name"),
            description=app_commands.locale_str("minigame_countingcmds_description"),
        )
        minigameCmds.add_command(countingCmds)
        self.bot.tree.add_command(minigameCmds)


async def setup(bot):
    await bot.add_cog(minigameCog(bot))
