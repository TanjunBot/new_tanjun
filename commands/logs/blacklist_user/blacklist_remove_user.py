from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, is_log_entity_blacklisted, remove_log_blacklist

async def blacklist_remove_user(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveUser.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistRemoveUser.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(user.id), LogBlacklistType.USER)
    if not is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveUser.notBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistRemoveUser.notBlacklisted.description(command_info.locale))
    else:
        await remove_log_blacklist(command_info.guild.id, str(user.id), LogBlacklistType.USER)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveUser.success.title(str(command_info.locale)), description=locale.commands.logs.blacklistRemoveUser.success.description(command_info.locale))
    await command_info.reply(embed=embed)