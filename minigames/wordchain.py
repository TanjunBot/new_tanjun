from locale_keys import locale as _locale
import discord
from api import check_if_opted_out, clear_wordchain, get_wordchain_last_user_id, get_wordchain_word, set_wordchain_word
from utility import DiscordSafe, EmbedColor, tanjunEmbed

async def wordchain(message: discord.Message) -> None:
    if message.guild is None:
        embed: discord.Embed = tanjunEmbed(colour=EmbedColor.ERROR, title=_locale.errors.guildonly.title('en_US'), description=_locale.errors.guildonly.description('en_US'))
        await DiscordSafe.send(message.channel, embed=embed)
        return
    wordchain_word = await get_wordchain_word(message.channel.id)
    if wordchain_word is None:
        return
    locale_str = str(message.guild.preferred_locale) if hasattr(message.guild, 'preferred_locale') else 'en_US'
    if await check_if_opted_out(message.author.id):
        await DiscordSafe.send_dm(message.author, _locale.minigames.wordchain.opted_out(locale_str))
        await DiscordSafe.delete(message)
        return
    content = message.content
    if not content:
        await DiscordSafe.delete(message)
        return
    if content.count(' ') > 0:
        await DiscordSafe.delete(message)
        return
    if str(await get_wordchain_last_user_id(message.channel.id)) == str(message.author.id):
        await DiscordSafe.delete(message)
        return
    end_chars = ('.', '?', '!', ';', ':')
    for char in content:
        if char in end_chars:
            await clear_wordchain(message.channel.id)
            await set_wordchain_word(channel_id=message.channel.id, guild_id=message.guild.id, word='', worder_id='nobody')
            embed = tanjunEmbed(colour=EmbedColor.SUCCESS, title=_locale.minigames.wordchain.finished.title(locale_str), description=_locale.minigames.wordchain.finished.description(locale_str, sentence=wordchain_word + content))
            await DiscordSafe.send(message.channel, embed=embed)
            return
    if content == ',':
        await set_wordchain_word(channel_id=message.channel.id, guild_id=message.guild.id, word=wordchain_word + ',', worder_id='nobody')
        return
    await set_wordchain_word(channel_id=message.channel.id, guild_id=message.guild.id, word=wordchain_word + ' ' + content, worder_id=message.author.id)