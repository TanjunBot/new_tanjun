from locale_keys import locale
import discord
import utility
from api import add_media_channel, check_if_opted_out, get_media_channel, remove_media_channel

async def addMediaChannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.missingPermission.title(command_info.locale), description=locale.commands.admin.channel.media.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(command_info.guild.me).manage_messages or not channel.permissions_for(command_info.guild.me).read_message_history:
        embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.missingPermission.title(command_info.locale), description=locale.commands.admin.channel.media.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await get_media_channel(command_info.guild.id):
        embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.alreadySet.title(str(command_info.locale)), description=locale.commands.admin.channel.media.alreadySet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await channel.send(embed=utility.tanjunEmbed(title=locale.commands.admin.channel.media.infoMessage.title(str(command_info.locale)), description=locale.commands.admin.channel.media.infoMessage.description(command_info.locale)))
    await add_media_channel(command_info.guild.id, channel.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.success.title(str(command_info.locale)), description=locale.commands.admin.channel.media.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)

async def removeMediaChannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.missingPermission.title(command_info.locale), description=locale.commands.admin.channel.media.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not await get_media_channel(channel.id):
        embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.notSet.title(str(command_info.locale)), description=locale.commands.admin.channel.media.notSet.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    await remove_media_channel(command_info.guild.id, channel.id)
    await channel.send(embed=utility.tanjunEmbed(title=locale.commands.admin.channel.media.infoMessageDelete.title(command_info.locale), description=locale.commands.admin.channel.media.infoMessageDelete.description(command_info.locale)))
    embed = utility.tanjunEmbed(title=locale.commands.admin.channel.media.deleteSuccess.title(str(command_info.locale)), description=locale.commands.admin.channel.media.deleteSuccess.description(str(command_info.locale)))
    await command_info.reply(embed=embed)

async def mediaChannelMessage(message: discord.Message) -> None:
    if not await get_media_channel(message.channel.id):
        return
    if await check_if_opted_out(message.author.id):
        await message.delete()
        await message.author.send(embed=utility.tanjunEmbed(title=locale.commands.admin.channel.media.optedOut.title(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en'), description=locale.commands.admin.channel.media.optedOut.description(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en')))
        return
    if len(message.attachments) > 0:
        return
    await message.delete()
    await message.author.send(embed=utility.tanjunEmbed(title=locale.commands.admin.channel.media.onlyMedia.title(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en'), description=locale.commands.admin.channel.media.onlyMedia.description(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en')))