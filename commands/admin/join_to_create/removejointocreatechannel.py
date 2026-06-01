from locale_keys import locale
import discord
import utility
from api import get_join_to_create_channel, remove_join_to_create_channel

async def removejointocreatechannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.admin.removejointocreatechannel.missingPermission.title(command_info.locale), description=locale.commands.admin.removejointocreatechannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not await get_join_to_create_channel(str(channel.id)):
        embed = utility.tanjunEmbed(title=locale.commands.admin.removejointocreatechannel.alreadySet.title(str(command_info.locale)), description=locale.commands.admin.removejointocreatechannel.alreadySet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await remove_join_to_create_channel(command_info.guild.id, channel.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.removejointocreatechannel.success.title(str(command_info.locale)), description=locale.commands.admin.removejointocreatechannel.success.description(command_info.locale))
    await command_info.reply(embed=embed)