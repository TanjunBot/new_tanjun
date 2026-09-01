from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, is_log_entity_blacklisted, remove_log_blacklist

async def blacklist_remove_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveRole.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistRemoveRole.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)
    if not is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveRole.notBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistRemoveRole.notBlacklisted.description(command_info.locale))
    else:
        await remove_log_blacklist(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveRole.success.title(str(command_info.locale)), description=locale.commands.logs.blacklistRemoveRole.success.description(command_info.locale))
    await command_info.reply(embed=embed)