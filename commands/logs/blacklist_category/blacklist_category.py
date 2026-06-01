from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, add_log_blacklist, is_log_entity_blacklisted

async def blacklist_category(command_info: utility.CommandInfo, channel: discord.CategoryChannel) -> None:
    if isinstance(command_info.user, discord.Member) and (not command_info.user.guild_permissions.administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistCategory.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistCategory.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(channel.id), LogBlacklistType.CATEGORY)
    if is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistCategory.alreadyBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistCategory.alreadyBlacklisted.description(command_info.locale))
    else:
        await add_log_blacklist(command_info.guild.id, str(channel.id), LogBlacklistType.CATEGORY)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistCategory.blacklisted.title(str(command_info.locale)), description=locale.commands.logs.blacklistCategory.blacklisted.description(command_info.locale))
    await command_info.reply(embed=embed)