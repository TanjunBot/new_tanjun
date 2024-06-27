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
from commands.level.change_levelup_message import (
    change_levelup_message as changeLevelupMessageCommand,
)
from commands.level.disable_levelup_message import (
    disable_levelup_message as disableLevelupMessageCommand,
)
from commands.level.enable_levelup_message import (
    enable_levelup_message as enableLevelupMessageCommand,
)
from commands.level.set_levelup_channel import (
    set_levelup_channel_command as setLevelupChannelCommand,
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

    @app_commands.command(
        name=app_commands.locale_str("level_changelevelupmessage_name"),
        description=app_commands.locale_str("level_changelevelupmessage_description"),
    )
    @app_commands.describe(
        new_message=app_commands.locale_str(
            "level_changelevelupmessage_params_newmessage_description"
        ),
    )
    async def changelevelupmessage(
        self, ctx, new_message: app_commands.Range[str, 1, 255]
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

        await changeLevelupMessageCommand(commandInfo, new_message)

    @app_commands.command(
        name=app_commands.locale_str("level_disablelevelupmessage_name"),
        description=app_commands.locale_str("level_disablelevelupmessage_description"),
    )
    async def disablelevelupmessage(self, ctx):
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

        await disableLevelupMessageCommand(commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("level_enablelevelupmessage_name"),
        description=app_commands.locale_str("level_enablelevelupmessage_description"),
    )
    async def enablelevelupmessage(self, ctx):
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

        await enableLevelupMessageCommand(commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("level_setlevelupchannel_name"),
        description=app_commands.locale_str("level_setlevelupchannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "level_setlevelupchannel_params_channel_description"
        ),
    )
    async def setlevelupchannel(
        self, ctx, channel: Optional[discord.TextChannel] = None
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

        await setLevelupChannelCommand(commandInfo, channel)


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
