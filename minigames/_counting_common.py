from locale_keys import locale as _locale
import random
import discord
from api import check_if_opted_out
from utility import DiscordSafe, EmbedColor, tanjunEmbed

async def _handle_guild_check(message: discord.Message) -> bool:
    """Returns True if the message should be ignored (no guild)."""
    if message.guild is not None:
        return False
    embed: discord.Embed = tanjunEmbed(colour=EmbedColor.ERROR, title=_locale.errors.guildonly.title('en_US'), description=_locale.errors.guildonly.description('en_US'))
    await DiscordSafe.send(message.channel, embed=embed)
    return True

def _get_locale(message: discord.Message) -> str:
    return str(message.guild.preferred_locale) if hasattr(message.guild, 'preferred_locale') else 'en_US'

async def _handle_opted_out(message: discord.Message, locale_str: str) -> bool:
    """Returns True if the user was opted out and the message was handled."""
    if not await check_if_opted_out(message.author.id):
        return False
    await DiscordSafe.send_dm(message.author, _locale.minigames.counting.opted_out(locale_str))
    await DiscordSafe.delete(message)
    return True

async def counting(message: discord.Message, *, get_progress_func, get_last_counter_id_func, increase_progress_func, on_failure=None, on_double_count=None, config: dict | None=None) -> None:
    """Shared counting logic parameterized by variant-specific API functions and callbacks.

    Parameters
    ----------
    get_progress_func : async callable(channel_id) -> int | None
    get_last_counter_id_func : async callable(channel_id) -> str | None
    increase_progress_func : async callable(channel_id, user_id) -> None
    on_failure : async callable(message, locale, correct_number) or None
        Called when the user sends an invalid number (empty, non-digit, or wrong).
        If None, the message is silently deleted (normal counting behavior).
    on_double_count : async callable(message, locale, correct_number) or None
        Called when the same user counts twice in a row.
        If None, the message is silently deleted (normal counting behavior).
    config : dict or None
        Pre-fetched config with 'progress' and 'last_counter_id'. If provided,
        get_progress_func and get_last_counter_id_func are not called.
    """
    if await _handle_guild_check(message):
        return
    if config is not None:
        progress = config.get('progress')
    else:
        progress = await get_progress_func(message.channel.id)
    locale_str = _get_locale(message)
    if not progress and progress != 0:
        return
    if await _handle_opted_out(message, locale_str):
        return
    content = message.content
    if not content:
        if on_failure:
            await on_failure(message, locale_str, progress + 1 if progress is not None else 0)
        else:
            await DiscordSafe.delete(message)
        return
    if not content.isdigit():
        if on_failure:
            await on_failure(message, locale_str, progress + 1 if progress is not None else 0)
        else:
            await DiscordSafe.delete(message)
        return
    number = int(content)
    if number != progress + 1:
        if on_failure:
            await on_failure(message, locale_str, progress + 1)
        else:
            await DiscordSafe.delete(message)
        return
    if config is not None:
        last_counter_id = config.get('last_counter_id')
    else:
        last_counter_id = await get_last_counter_id_func(message.channel.id)
    if last_counter_id == str(message.author.id):
        if on_double_count:
            await on_double_count(message, locale_str, progress + 1)
        else:
            await DiscordSafe.delete(message)
        return
    await increase_progress_func(message.channel.id, message.author.id)
    if random.randint(1, 100) == 1:
        await DiscordSafe.send(message.channel, embed=tanjunEmbed(description=str(progress + 2)))
        await increase_progress_func(message.channel.id, 'me')