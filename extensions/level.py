import discord
from discord.ext import commands
from discord import app_commands
import utility
from utility import tanjunEmbed
from localizer import tanjunLocalizer
from typing import List, Optional

from commands.level.disable_level_system import (
    disable_level_system as disableLevelSystemCommand,
)
from commands.level.enable_level_system import (
    enable_level_system as enableLevelSystemCommand,
)


class LevelConfigCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("level_disable_name"),
        description=app_commands.locale_str("level_disable_description"),
    )
    async def disablelevelsystem(self, ctx):
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

        await disableLevelSystemCommand(commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("level_enable_name"),
        description=app_commands.locale_str("level_enable_description"),
    )
    async def enablelevelsystem(self, ctx):
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

        await enableLevelSystemCommand(commandInfo)


class levelCommands(discord.app_commands.Group): ...


class levelCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        levelCmds = levelCommands(name="levelcommands", description="Level Commands")
        levelConfigCmds = LevelConfigCommands(
            name=app_commands.locale_str("level_config_name"),
            description=app_commands.locale_str("level_config_description"),
        )
        levelCmds.add_command(levelConfigCmds)
        self.bot.tree.add_command(levelCmds)


async def setup(bot):
    await bot.add_cog(levelCog(bot))
