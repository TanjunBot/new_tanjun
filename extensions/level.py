import discord
from discord.ext import commands
from discord import app_commands
import utility
from utility import tanjunEmbed, LEVEL_SCALINGS
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
from commands.level.change_xp_scaling import change_xp_scaling_command, show_xp_scalings
from commands.level.add_level_role import add_level_role_command
from commands.level.remove_level_role import remove_level_role_command
from commands.level.show_level_roles import show_level_roles_command


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

    @app_commands.command(
        name=app_commands.locale_str("level_changexpscaling_name"),
        description=app_commands.locale_str("level_changexpscaling_description"),
    )
    @app_commands.describe(
        scaling=app_commands.locale_str(
            "level_changexpscaling_params_scaling_description"
        ),
        customformula=app_commands.locale_str(
            "level_changexpscaling_params_customformula_description"
        ),
    )
    @app_commands.choices(
        scaling=[
            app_commands.Choice(name=key, value=key)
            for key in list(LEVEL_SCALINGS.keys()) + ["custom"]
        ]
    )
    async def changexpscaling(
        self, ctx, scaling: str, customformula: Optional[str] = None
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

        await change_xp_scaling_command(commandInfo, scaling, customformula)

    @app_commands.command(
        name=app_commands.locale_str("level_showxpscalings_name"),
        description=app_commands.locale_str("level_showxpscalings_description"),
    )
    @app_commands.describe(
        startlevel=app_commands.locale_str(
            "level_showxpscalings_params_startlevel_description"
        ),
        endlevel=app_commands.locale_str(
            "level_showxpscalings_params_endlevel_description"
        ),
    )
    async def showxpscalings(self, ctx, startlevel: int = 1, endlevel: int = 5):
        await ctx.response.defer()
        commandInfo = utility.commandInfo(
            user=ctx.user,
            channel=ctx.channel,
            guild=ctx.guild,
            command=ctx.command,
            locale=ctx.locale,
            message=await ctx.original_response(),
            permissions=ctx.permissions,
            reply=ctx.followup.send,
            client=ctx.client,
        )

        await show_xp_scalings(commandInfo, startlevel, endlevel)

    @app_commands.command(
        name=app_commands.locale_str("level_addlevelrole_name"),
        description=app_commands.locale_str("level_addlevelrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_addlevelrole_params_role_description"),
        level=app_commands.locale_str("level_addlevelrole_params_level_description"),
    )
    async def addlevelrole(self, ctx, role: discord.Role, level: int):
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

        await add_level_role_command(commandInfo, role, level)

    @app_commands.command(
        name=app_commands.locale_str("level_removelevelrole_name"),
        description=app_commands.locale_str("level_removelevelrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_removelevelrole_params_role_description"),
        level=app_commands.locale_str("level_removelevelrole_params_level_description"),
    )
    async def removelevelrole(self, ctx, role: discord.Role, level: int):
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

        await remove_level_role_command(commandInfo, role, level)

    @app_commands.command(
        name=app_commands.locale_str("level_showlevelroles_name"),
        description=app_commands.locale_str("level_showlevelroles_description"),
    )
    async def showlevelroles(self, ctx):
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

        await show_level_roles_command(commandInfo)


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
