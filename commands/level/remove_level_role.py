from locale_keys import locale
import discord
from api import get_level_role, remove_level_role
from utility import CommandInfo, tanjunEmbed

async def remove_level_role_command(command_info: CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = tanjunEmbed(title=locale.commands.level.removelevelrole.error.no_permission.title(str(command_info.locale)), description=locale.commands.level.removelevelrole.error.no_permission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    existing_role = await get_level_role(str(command_info.guild.id), str(role.id))
    if not existing_role:
        embed = tanjunEmbed(title=locale.commands.level.removelevelrole.error.role_not_found.title(str(command_info.locale)), description=locale.commands.level.removelevelrole.error.role_not_found.description(str(command_info.locale), role=role.mention))
        await command_info.reply(embed=embed)
        return
    await remove_level_role(str(command_info.guild.id), str(role.id))
    embed = tanjunEmbed(title=locale.commands.level.removelevelrole.success.title(str(command_info.locale)), description=locale.commands.level.removelevelrole.success.description(str(command_info.locale), role=role.mention))
    await command_info.reply(embed=embed)