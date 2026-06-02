from locale_keys import locale
from typing import cast
import discord
from discord import app_commands
from discord.ext import commands
import utility
from commands.level.add_level_role import add_level_role_command
from commands.level.change_levelup_message import change_levelup_message as changeLevelupMessageCommand
from commands.level.change_xp_scaling import change_xp_scaling_command, show_xp_scalings
from commands.level.disable_level_system import disable_level_system as disableLevelSystemCommand
from commands.level.disable_levelup_message import disable_levelup_message as disableLevelupMessageCommand
from commands.level.enable_level_system import enable_level_system as enableLevelSystemCommand
from commands.level.enable_levelup_message import enable_levelup_message as enableLevelupMessageCommand
from commands.level.give_xp import give_xp_command
from commands.level.leaderboard import leaderboard as leaderboard_command
from commands.level.level_blacklist import add_channel_to_blacklist_command, add_role_to_blacklist_command, add_user_to_blacklist_command, remove_channel_from_blacklist_command, remove_role_from_blacklist_command, remove_user_from_blacklist_command, show_blacklist_command
from commands.level.level_boosts import add_channel_boost_command, add_role_boost_command, add_user_boost_command, calculate_user_channel_boost_command, remove_channel_boost_command, remove_role_boost_command, remove_user_boost_command, show_boosts_command
from commands.level.level_rankcard import set_background_command, show_rankcard_command
from commands.level.level_set_xp_cooldown import set_text_cooldown_command, set_voice_cooldown_command
from commands.level.remove_level_role import remove_level_role_command
from commands.level.set_levelup_channel import set_levelup_channel_command as setLevelupChannelCommand
from commands.level.show_level_roles import show_level_roles_command
from commands.level.take_xp import take_xp_command
from utility import LEVEL_SCALINGS

class BlacklistCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.level.blacklist.addc.name.discord_key, description=locale.level.blacklist.addc.description.discord_key)
    @app_commands.describe(channel=locale.level.blacklist.addc.params.channel.description.discord_key, reason=locale.level.blacklist.addc.params.reason.description.discord_key)
    async def add_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, reason: app_commands.Range[str, 1, 100] | None=None) -> None:
        from typing import cast
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_channel_to_blacklist_command(command_info, channel, reason)

    @app_commands.command(name=locale.level.blacklist.removec.name.discord_key, description=locale.level.blacklist.removec.description.discord_key)
    @app_commands.describe(channel=locale.level.blacklist.removec.params.channel.description.discord_key)
    async def remove_channel(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_channel_from_blacklist_command(command_info, channel)

    @app_commands.command(name=locale.level.blacklist.addr.name.discord_key, description=locale.level.blacklist.addr.description.discord_key)
    @app_commands.describe(role=locale.level.blacklist.addr.params.role.description.discord_key, reason=locale.level.blacklist.addr.params.reason.description.discord_key)
    async def add_role(self, interaction: discord.Interaction, role: discord.Role, reason: app_commands.Range[str, 1, 100] | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_role_to_blacklist_command(command_info, role, reason)

    @app_commands.command(name=locale.level.blacklist.remover.name.discord_key, description=locale.level.blacklist.remover.description.discord_key)
    @app_commands.describe(role=locale.level.blacklist.remover.params.role.description.discord_key)
    async def remove_role(self, interaction: discord.Interaction, role: discord.Role) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_role_from_blacklist_command(command_info, role)

    @app_commands.command(name=locale.level.blacklist.addu.name.discord_key, description=locale.level.blacklist.addu.description.discord_key)
    @app_commands.describe(user=locale.level.blacklist.addu.params.user.description.discord_key, reason=locale.level.blacklist.addu.params.reason.description.discord_key)
    async def add_user(self, interaction: discord.Interaction, user: discord.Member, reason: app_commands.Range[str, 1, 100] | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_user_to_blacklist_command(command_info, user, reason)

    @app_commands.command(name=locale.level.blacklist.removeu.name.discord_key, description=locale.level.blacklist.removeu.description.discord_key)
    @app_commands.describe(user=locale.level.blacklist.removeu.params.user.description.discord_key)
    async def remove_user(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_user_from_blacklist_command(command_info, user)

    @app_commands.command(name=locale.level.blacklist.show.name.discord_key, description=locale.level.blacklist.show.description.discord_key)
    async def show(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_blacklist_command(command_info)

class LevelBoostCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.level.boosts.addrole.name.discord_key, description=locale.level.boosts.addrole.description.discord_key)
    @app_commands.describe(role=locale.level.boosts.addrole.params.role.description.discord_key, boost=locale.level.boosts.addrole.params.boost.description.discord_key, additive=locale.level.boosts.addrole.params.additive.description.discord_key)
    async def add_role_boost(self, interaction: discord.Interaction, role: discord.Role, boost: app_commands.Range[float, 0.1, 10.0], additive: bool) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_role_boost_command(command_info, role, boost, additive)

    @app_commands.command(name=locale.level.boosts.addchannel.name.discord_key, description=locale.level.boosts.addchannel.description.discord_key)
    @app_commands.describe(channel=locale.level.boosts.addchannel.params.channel.description.discord_key, boost=locale.level.boosts.addchannel.params.boost.description.discord_key, additive=locale.level.boosts.addchannel.params.additive.description.discord_key)
    async def add_channel_boost(self, interaction: discord.Interaction, channel: discord.TextChannel, boost: app_commands.Range[float, 0.1, 10.0], additive: bool) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_channel_boost_command(command_info, channel, boost, additive)

    @app_commands.command(name=locale.level.boosts.adduser.name.discord_key, description=locale.level.boosts.adduser.description.discord_key)
    @app_commands.describe(user=locale.level.boosts.adduser.params.user.description.discord_key, boost=locale.level.boosts.adduser.params.boost.description.discord_key, additive=locale.level.boosts.adduser.params.additive.description.discord_key)
    async def add_user_boost(self, interaction: discord.Interaction, user: discord.Member, boost: app_commands.Range[float, 0.1, 10.0], additive: bool) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_user_boost_command(command_info, user, boost, additive)

    @app_commands.command(name=locale.level.boosts.removerole.name.discord_key, description=locale.level.boosts.removerole.description.discord_key)
    @app_commands.describe(role=locale.level.boosts.removerole.params.role.description.discord_key)
    async def remove_role_boost(self, interaction: discord.Interaction, role: discord.Role) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_role_boost_command(command_info, role)

    @app_commands.command(name=locale.level.boosts.removechannel.name.discord_key, description=locale.level.boosts.removechannel.description.discord_key)
    @app_commands.describe(channel=locale.level.boosts.removechannel.params.channel.description.discord_key)
    async def remove_channel_boost(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_channel_boost_command(command_info, channel)

    @app_commands.command(name=locale.level.boosts.removeuser.name.discord_key, description=locale.level.boosts.removeuser.description.discord_key)
    @app_commands.describe(user=locale.level.boosts.removeuser.params.user.description.discord_key)
    async def remove_user_boost(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_user_boost_command(command_info, user)

    @app_commands.command(name=locale.level.boosts.show.name.discord_key, description=locale.level.boosts.show.description.discord_key)
    async def show_boosts(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_boosts_command(command_info)

    @app_commands.command(name=locale.level.boosts.calculate.name.discord_key, description=locale.level.boosts.calculate.description.discord_key)
    @app_commands.describe(user=locale.level.boosts.calculate.params.user.description.discord_key, channel=locale.level.boosts.calculate.params.channel.description.discord_key)
    async def calculate_user_channel_boost(self, interaction: discord.Interaction, user: discord.Member, channel: discord.TextChannel) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await calculate_user_channel_boost_command(command_info, user, channel)

class LevelConfigCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.level.disable.name.discord_key, description=locale.level.disable.description.discord_key)
    async def disablelevelsystem(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await disableLevelSystemCommand(command_info)

    @app_commands.command(name=locale.level.enable.name.discord_key, description=locale.level.enable.description.discord_key)
    async def enablelevelsystem(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await enableLevelSystemCommand(command_info)

    @app_commands.command(name=locale.level.changelevelupmessage.name.discord_key, description=locale.level.changelevelupmessage.description.discord_key)
    @app_commands.describe(newmessage=locale.level.changelevelupmessage.params.newmessage.description.discord_key)
    async def changelevelupmessage(self, interaction: discord.Interaction, newmessage: app_commands.Range[str, 1, 255]) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await changeLevelupMessageCommand(command_info, newmessage)

    @app_commands.command(name=locale.level.disablelevelupmessage.name.discord_key, description=locale.level.disablelevelupmessage.description.discord_key)
    async def disablelevelupmessage(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await disableLevelupMessageCommand(command_info)

    @app_commands.command(name=locale.level.enablelevelupmessage.name.discord_key, description=locale.level.enablelevelupmessage.description.discord_key)
    async def enablelevelupmessage(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await enableLevelupMessageCommand(command_info)

    @app_commands.command(name=locale.level.setlevelupchannel.name.discord_key, description=locale.level.setlevelupchannel.description.discord_key)
    @app_commands.describe(channel=locale.level.setlevelupchannel.params.channel.description.discord_key)
    async def setlevelupchannel(self, interaction: discord.Interaction, channel: discord.TextChannel | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await setLevelupChannelCommand(command_info, channel)

    @app_commands.command(name=locale.level.changexpscaling.name.discord_key, description=locale.level.changexpscaling.description.discord_key)
    @app_commands.describe(scaling=locale.level.changexpscaling.params.scaling.description.discord_key, customformula=locale.level.changexpscaling.params.customformula.description.discord_key)
    @app_commands.choices(scaling=[app_commands.Choice(name=key, value=key) for key in list(LEVEL_SCALINGS.keys()) + ['custom']])
    async def changexpscaling(self, interaction: discord.Interaction, scaling: str, customformula: str | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await change_xp_scaling_command(command_info, scaling, customformula)

    @app_commands.command(name=locale.level.showxpscalings.name.discord_key, description=locale.level.showxpscalings.description.discord_key)
    @app_commands.describe(startlevel=locale.level.showxpscalings.params.startlevel.description.discord_key, endlevel=locale.level.showxpscalings.params.endlevel.description.discord_key)
    async def showxpscalings(self, interaction: discord.Interaction, startlevel: int=1, endlevel: int=5) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=await interaction.original_response(), permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_xp_scalings(command_info, startlevel, endlevel)

    @app_commands.command(name=locale.level.addlevelrole.name.discord_key, description=locale.level.addlevelrole.description.discord_key)
    @app_commands.describe(role=locale.level.addlevelrole.params.role.description.discord_key, level=locale.level.addlevelrole.params.level.description.discord_key)
    async def addlevelrole(self, interaction: discord.Interaction, role: discord.Role, level: int) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await add_level_role_command(command_info, role, level)

    @app_commands.command(name=locale.level.removelevelrole.name.discord_key, description=locale.level.removelevelrole.description.discord_key)
    @app_commands.describe(role=locale.level.removelevelrole.params.role.description.discord_key)
    async def removelevelrole(self, interaction: discord.Interaction, role: discord.Role) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await remove_level_role_command(command_info, role)

    @app_commands.command(name=locale.level.showlevelroles.name.discord_key, description=locale.level.showlevelroles.description.discord_key)
    async def showlevelroles(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_level_roles_command(command_info)

    @app_commands.command(name=locale.level.givexp.name.discord_key, description=locale.level.givexp.description.discord_key)
    @app_commands.describe(user=locale.level.givexp.params.user.description.discord_key, amount=locale.level.givexp.params.amount.description.discord_key)
    async def give_xp(self, interaction: discord.Interaction, user: discord.Member, amount: int) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await give_xp_command(command_info, user, amount)

    @app_commands.command(name=locale.level.takexp.name.discord_key, description=locale.level.takexp.description.discord_key)
    @app_commands.describe(user=locale.level.takexp.params.user.description.discord_key, amount=locale.level.takexp.params.amount.description.discord_key)
    async def take_xp(self, interaction: discord.Interaction, user: discord.Member, amount: int) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await take_xp_command(command_info, user, amount)

    @app_commands.command(name=locale.level.settextcooldown.name.discord_key, description=locale.level.settextcooldown.description.discord_key)
    @app_commands.describe(cooldown=locale.level.settextcooldown.params.cooldown.description.discord_key)
    async def settextcooldown(self, interaction: discord.Interaction, cooldown: int) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await set_text_cooldown_command(command_info, cooldown)

    @app_commands.command(name=locale.level.setvoicecooldown.name.discord_key, description=locale.level.setvoicecooldown.description.discord_key)
    @app_commands.describe(cooldown=locale.level.setvoicecooldown.params.cooldown.description.discord_key)
    async def setvoicecooldown(self, interaction: discord.Interaction, cooldown: int) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await set_voice_cooldown_command(command_info, cooldown)

class levelCommands(discord.app_commands.Group):

    @app_commands.command(name=locale.level.rank.name.discord_key, description=locale.level.rank.description.discord_key)
    @app_commands.describe(user=locale.level.rank.params.user.description.discord_key)
    async def rankcard(self, interaction: discord.Interaction, user: discord.Member | None=None) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await show_rankcard_command(command_info, user or cast(discord.Member, interaction.user))

    @app_commands.command(name=locale.level.setbackground.name.discord_key, description=locale.level.setbackground.description.discord_key)
    @app_commands.describe(image=locale.level.setbackground.params.image.description.discord_key)
    async def set_background(self, interaction: discord.Interaction, image: discord.Attachment) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=interaction.message, permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await set_background_command(command_info, image)

    @app_commands.command(name=locale.level.leaderboard.name.discord_key, description=locale.level.leaderboard.description.discord_key)
    @app_commands.describe(page=locale.level.leaderboard.params.page.description.discord_key)
    async def leaderboard(self, interaction: discord.Interaction, page: int=1) -> None:
        await interaction.response.defer()
        command_info = utility.command_info(user=interaction.user, channel=cast(discord.abc.GuildChannel, interaction.channel), guild=interaction.guild, command=interaction.command, locale=interaction.locale, message=await interaction.original_response(), permissions=interaction.permissions, reply=interaction.followup.send, client=interaction.client)
        await leaderboard_command(command_info, page)

class levelCog(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        level_cmds = levelCommands(name=locale.levelcommands.name.discord_key, description=locale.levelcommands.description.discord_key)
        level_config_cmds = LevelConfigCommands(name=locale.level.config.name.discord_key, description=locale.level.config.description.discord_key)
        level_boost_cmds = LevelBoostCommands(name=locale.level.boosts.name.discord_key, description=locale.level.boosts.description.discord_key)
        blacklist = BlacklistCommands(name=locale.level.blacklist.name.discord_key, description=locale.level.blacklist.description.discord_key)
        level_cmds.add_command(level_config_cmds)
        level_cmds.add_command(level_boost_cmds)
        level_cmds.add_command(blacklist)
        self.bot.tree.add_command(level_cmds)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(levelCog(bot))