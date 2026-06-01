from locale_keys import locale
import discord
from api import add_level_role, get_level_roles
from utility import CommandInfo, tanjunEmbed

async def add_level_role_command(command_info: CommandInfo, role: discord.Role, level: int) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = tanjunEmbed(title=locale.commands.level.addlevelrole.error.no_permission.title(str(command_info.locale)), description=locale.commands.level.addlevelrole.error.no_permission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if level < 1:
        embed = tanjunEmbed(title=locale.commands.level.addlevelrole.error.invalid_level.title(str(command_info.locale)), description=locale.commands.level.addlevelrole.error.invalid_level.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    level_roles = [lr async for lr in get_level_roles(str(command_info.guild.id))]
    if role.id in [int(lr.role_id) for lr in level_roles]:
        embed = tanjunEmbed(title=locale.commands.level.addlevelrole.error.role_exists.title(str(command_info.locale)), description=locale.commands.level.addlevelrole.error.role_exists.description(str(command_info.locale), role=role.mention))
        await command_info.reply(embed=embed)
        return
    await add_level_role(str(command_info.guild.id), str(role.id), level)
    embed = tanjunEmbed(title=locale.commands.level.addlevelrole.success.title(str(command_info.locale)), description=locale.commands.level.addlevelrole.success.description(str(command_info.locale), role=role.mention, level=level))
    await command_info.reply(embed=embed)