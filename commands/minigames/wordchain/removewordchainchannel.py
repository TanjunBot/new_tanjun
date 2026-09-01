from locale_keys import locale
import discord
from api import clear_wordchain, get_wordchain_word
from utility import CommandInfo, tanjunEmbed

async def removewordchainchannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        return
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).moderate_members):
        embed = tanjunEmbed(title=locale.minigames.removewordchainchannel.error.no_moderate_members_perms.title(command_info.locale), description=locale.minigames.removewordchainchannel.error.no_moderate_members_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    current_progress = await get_wordchain_word(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(title=locale.minigames.removewordchainchannel.error.not_counting_channel.title(command_info.locale), description=locale.minigames.removewordchainchannel.error.not_counting_channel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await clear_wordchain(channel.id)
    embed = tanjunEmbed(title=locale.minigames.removewordchainchannel.success.title(str(command_info.locale)), description=locale.minigames.removewordchainchannel.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)
    info_embed = tanjunEmbed(title=locale.minigames.removewordchainchannel.channel_message.title(str(command_info.locale)), description=locale.minigames.removewordchainchannel.channel_message.description(command_info.locale))
    await channel.send(embed=info_embed)