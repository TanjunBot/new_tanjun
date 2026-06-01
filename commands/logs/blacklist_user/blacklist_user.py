from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, add_log_blacklist, is_log_entity_blacklisted

async def blacklist_user(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistUser.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistUser.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(user.id), LogBlacklistType.USER)
    if is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistUser.alreadyBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistUser.alreadyBlacklisted.description(command_info.locale))
    else:
        await add_log_blacklist(command_info.guild.id, str(user.id), LogBlacklistType.USER)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistUser.blacklisted.title(str(command_info.locale)), description=locale.commands.logs.blacklistUser.blacklisted.description(command_info.locale))
    await command_info.reply(embed=embed)