from locale_keys import locale
import discord
import utility
from api import LogBlacklistType, is_log_entity_blacklisted, remove_log_blacklist

async def blacklist_remove_voice(command_info: utility.CommandInfo, channel: discord.VoiceChannel) -> None:
    if isinstance(command_info.user, discord.Member) and (not command_info.user.guild_permissions.administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveVoiceChannel.missingPermission.title(command_info.locale), description=locale.commands.logs.blacklistRemoveVoiceChannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    is_blacklisted = await is_log_entity_blacklisted(command_info.guild.id, str(channel.id), LogBlacklistType.VOICE_CHANNEL)
    if not is_blacklisted:
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveVoiceChannel.notBlacklisted.title(command_info.locale), description=locale.commands.logs.blacklistRemoveVoiceChannel.notBlacklisted.description(command_info.locale))
    else:
        await remove_log_blacklist(command_info.guild.id, str(channel.id), LogBlacklistType.VOICE_CHANNEL)
        embed = utility.tanjunEmbed(title=locale.commands.logs.blacklistRemoveVoiceChannel.success.title(str(command_info.locale)), description=locale.commands.logs.blacklistRemoveVoiceChannel.success.description(command_info.locale))
    await command_info.reply(embed=embed)