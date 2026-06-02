from locale_keys import locale
import discord
import utility
from api import get_log_channel as get_log_channel_api
from api import remove_log_channel as remove_log_channel_api

async def remove_log_channel(command_info: utility.CommandInfo) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.logs.removeLogChannel.missingPermission.title(command_info.locale), description=locale.commands.logs.removeLogChannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    log_channel = await get_log_channel_api(command_info.guild.id)
    if not log_channel:
        embed = utility.tanjunEmbed(title=locale.commands.logs.removeLogChannel.notSet.title(str(command_info.locale)), description=locale.commands.logs.removeLogChannel.notSet.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    await remove_log_channel_api(command_info.guild.id)
    embed = utility.tanjunEmbed(title=locale.commands.logs.removeLogChannel.success.title(str(command_info.locale)), description=locale.commands.logs.removeLogChannel.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)