from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, add_log_blacklist, is_log_entity_blacklisted

async def blacklist_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRole.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistRole.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)
    if is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRole.alreadyBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistRole.alreadyBlacklisted.description(command_info.locale))
    else:
        await add_log_blacklist(command_info.guild.id, str(role.id), LogBlacklistType.ROLE)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRole.blacklisted.title(str(command_info.locale)), description=locale.commands.logs.blacklistRole.blacklisted.description(command_info.locale))
    await command_info.reply(embed=embed)