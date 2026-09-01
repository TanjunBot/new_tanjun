from locale_keys import locale
import discord
import utility
from api import get_join_to_create_channel, set_join_to_create_channel

async def jointocreatechannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.admin.jointocreatechannel.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.jointocreatechannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await get_join_to_create_channel(str(channel.id)):
        embed = utility.tanjunEmbed(title=locale.commands.admin.jointocreatechannel.alreadySet.title(str(command_info.locale)), description=locale.commands.admin.jointocreatechannel.alreadySet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await set_join_to_create_channel(command_info.guild.id, channel.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.jointocreatechannel.success.title(str(command_info.locale)), description=locale.commands.admin.jointocreatechannel.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)