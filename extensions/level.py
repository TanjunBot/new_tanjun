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
from commands.level.level_boosts import (
    add_role_boost_command,
    add_channel_boost_command,
    add_user_boost_command,
    remove_role_boost_command,
    remove_channel_boost_command,
    remove_user_boost_command,
    show_boosts_command,
    calculate_user_channel_boost_command,
)
from commands.level.level_blacklist import (
    add_channel_to_blacklist_command,
    remove_channel_from_blacklist_command,
    add_role_to_blacklist_command,
    remove_role_from_blacklist_command,
    add_user_to_blacklist_command,
    remove_user_from_blacklist_command,
    show_blacklist_command,
)
from commands.level.level_rankcard import (
    show_rankcard_command,
    set_background_command,
)
from commands.level.give_xp import give_xp_command 
from commands.level.take_xp import take_xp_command


class BlacklistCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_addc_name"),
        description=app_commands.locale_str("level_blacklist_addc_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "level_blacklist_addc_params_channel_description"
        ),
        reason=app_commands.locale_str(
            "level_blacklist_addc_params_reason_description"
        ),
    )
    async def add_channel(self, ctx, channel: discord.TextChannel, reason: str = None):
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
        await add_channel_to_blacklist_command(commandInfo, channel, reason)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_removec_name"),
        description=app_commands.locale_str("level_blacklist_removec_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "level_blacklist_removec_params_channel_description"
        ),
    )
    async def remove_channel(self, ctx, channel: discord.TextChannel):
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
        await remove_channel_from_blacklist_command(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_addr_name"),
        description=app_commands.locale_str("level_blacklist_addr_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_blacklist_addr_params_role_description"),
        reason=app_commands.locale_str(
            "level_blacklist_addr_params_reason_description"
        ),
    )
    async def add_role(self, ctx, role: discord.Role, reason: str = None):
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
        await add_role_to_blacklist_command(commandInfo, role, reason)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_remover_name"),
        description=app_commands.locale_str("level_blacklist_remover_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_blacklist_remover_params_role_description"),
    )
    async def remove_role(self, ctx, role: discord.Role):
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
        await remove_role_from_blacklist_command(commandInfo, role)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_addu_name"),
        description=app_commands.locale_str("level_blacklist_addu_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_blacklist_addu_params_user_description"),
        reason=app_commands.locale_str(
            "level_blacklist_addu_params_reason_description"
        ),
    )
    async def add_user(self, ctx, user: discord.Member, reason: str = None):
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
        await add_user_to_blacklist_command(commandInfo, user, reason)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_removeu_name"),
        description=app_commands.locale_str("level_blacklist_removeu_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_blacklist_removeu_params_user_description"),
    )
    async def remove_user(self, ctx, user: discord.Member):
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
        await remove_user_from_blacklist_command(commandInfo, user)

    @app_commands.command(
        name=app_commands.locale_str("level_blacklist_show_name"),
        description=app_commands.locale_str("level_blacklist_show_description"),
    )
    async def show(self, ctx):
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
        await show_blacklist_command(commandInfo)


class LevelBoostCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("level_boosts_addrole_name"),
        description=app_commands.locale_str("level_boosts_addrole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_boosts_addrole_params_role_description"),
        boost=app_commands.locale_str("level_boosts_addrole_params_boost_description"),
        additive=app_commands.locale_str(
            "level_boosts_addrole_params_additive_description"
        ),
    )
    async def add_role_boost(
        self, ctx, role: discord.Role, boost: float, additive: bool
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
        await add_role_boost_command(commandInfo, role, boost, additive)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_addchannel_name"),
        description=app_commands.locale_str("level_boosts_addchannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "level_boosts_addchannel_params_channel_description"
        ),
        boost=app_commands.locale_str(
            "level_boosts_addchannel_params_boost_description"
        ),
        additive=app_commands.locale_str(
            "level_boosts_addchannel_params_additive_description"
        ),
    )
    async def add_channel_boost(
        self, ctx, channel: discord.TextChannel, boost: float, additive: bool
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
        await add_channel_boost_command(commandInfo, channel, boost, additive)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_adduser_name"),
        description=app_commands.locale_str("level_boosts_adduser_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_boosts_adduser_params_user_description"),
        boost=app_commands.locale_str("level_boosts_adduser_params_boost_description"),
        additive=app_commands.locale_str(
            "level_boosts_adduser_params_additive_description"
        ),
    )
    async def add_user_boost(
        self, ctx, user: discord.Member, boost: float, additive: bool
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
        await add_user_boost_command(commandInfo, user, boost, additive)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_removerole_name"),
        description=app_commands.locale_str("level_boosts_removerole_description"),
    )
    @app_commands.describe(
        role=app_commands.locale_str("level_boosts_removerole_params_role_description"),
    )
    async def remove_role_boost(self, ctx, role: discord.Role):
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
        await remove_role_boost_command(commandInfo, role)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_removechannel_name"),
        description=app_commands.locale_str("level_boosts_removechannel_description"),
    )
    @app_commands.describe(
        channel=app_commands.locale_str(
            "level_boosts_removechannel_params_channel_description"
        ),
    )
    async def remove_channel_boost(self, ctx, channel: discord.TextChannel):
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
        await remove_channel_boost_command(commandInfo, channel)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_removeuser_name"),
        description=app_commands.locale_str("level_boosts_removeuser_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_boosts_removeuser_params_user_description"),
    )
    async def remove_user_boost(self, ctx, user: discord.Member):
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
        await remove_user_boost_command(commandInfo, user)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_show_name"),
        description=app_commands.locale_str("level_boosts_show_description"),
    )
    async def show_boosts(self, ctx):
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
        await show_boosts_command(commandInfo)

    @app_commands.command(
        name=app_commands.locale_str("level_boosts_calculate_name"),
        description=app_commands.locale_str("level_boosts_calculate_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_boosts_calculate_params_user_description"),
        channel=app_commands.locale_str(
            "level_boosts_calculate_params_channel_description"
        ),
    )
    async def calculate_user_channel_boost(
        self, ctx, user: discord.Member, channel: discord.TextChannel
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
        await calculate_user_channel_boost_command(commandInfo, user, channel)


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

    @app_commands.command(
        name=app_commands.locale_str("level_givexp_name"),
        description=app_commands.locale_str("level_givexp_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_givexp_params_user_description"),
        amount=app_commands.locale_str("level_givexp_params_amount_description"),
    )
    async def give_xp(self, ctx, user: discord.Member, amount: int):
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
        await give_xp_command(commandInfo, user, amount)

    @app_commands.command(
        name=app_commands.locale_str("level_takexp_name"),
        description=app_commands.locale_str("level_takexp_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_takexp_params_user_description"),
        amount=app_commands.locale_str("level_takexp_params_amount_description"),
    )
    async def take_xp(self, ctx, user: discord.Member, amount: int):
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
        await take_xp_command(commandInfo, user, amount)


class levelCommands(discord.app_commands.Group):
    @app_commands.command(
        name=app_commands.locale_str("level_rank_name"),
        description=app_commands.locale_str("level_rank_description"),
    )
    @app_commands.describe(
        user=app_commands.locale_str("level_rank_params_user_description"),
    )
    async def rankcard(self, ctx, user: discord.Member = None):
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
        await show_rankcard_command(commandInfo, user or ctx.user)

    @app_commands.command(
        name=app_commands.locale_str("level_setbackground_name"),
        description=app_commands.locale_str("level_setbackground_description"),
    )
    @app_commands.describe(
        image=app_commands.locale_str("level_setbackground_params_image_description"),
    )
    async def set_background(self, ctx, image: discord.Attachment):
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
        await set_background_command(commandInfo, image)


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
        levelBoostCmds = LevelBoostCommands(
            name=app_commands.locale_str("level_boosts_name"),
            description=app_commands.locale_str("level_boosts_description"),
        )

        blacklist = BlacklistCommands(
            name=app_commands.locale_str("level_blacklist_name"),
            description=app_commands.locale_str("level_blacklist_description"),
        )
        levelCmds.add_command(levelConfigCmds)
        levelCmds.add_command(levelBoostCmds)
        levelCmds.add_command(blacklist)
        self.bot.tree.add_command(levelCmds)


async def setup(bot):
    await bot.add_cog(levelCog(bot))
