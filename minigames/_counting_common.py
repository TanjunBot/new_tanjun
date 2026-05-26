import random

import discord

from api import check_if_opted_out
from localizer import tanjunLocalizer
from utility import tanjunEmbed


async def _handle_guild_check(message: discord.Message) -> bool:
    """Returns True if the message should be ignored (no guild)."""
    if message.guild is not None:
        return False

    embed: discord.Embed = tanjunEmbed(
        title=tanjunLocalizer.localize("en_US", "errors.guildonly.title"),
        description=tanjunLocalizer.localize("en_US", "errors.guildonly.description"),
    )
    await message.channel.send(embed=embed)
    return True


def _get_locale(message: discord.Message) -> str:
    return str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"


async def _handle_opted_out(message: discord.Message, locale: str) -> bool:
    """Returns True if the user was opted out and the message was handled."""
    if not await check_if_opted_out(message.author.id):
        return False

    try:
        await message.author.send(tanjunLocalizer.localize(locale, "minigames.counting.opted_out"))
    except discord.Forbidden:
        pass
    await message.delete()
    return True


async def counting(
    message: discord.Message,
    *,
    get_progress_func,
    get_last_counter_id_func,
    increase_progress_func,
    on_failure=None,
    on_double_count=None,
    config: dict | None = None,
) -> None:
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
    if message.author.bot:
        return

    if await _handle_guild_check(message):
        return

    if config is not None:
        progress = config.get("progress")
    else:
        progress = await get_progress_func(message.channel.id)
    locale = _get_locale(message)

    if not progress and progress != 0:
        return

    if await _handle_opted_out(message, locale):
        return

    content = message.content

    if not content:
        if on_failure:
            await on_failure(message, locale, progress + 1 if progress is not None else 0)
        else:
            await message.delete()
        return

    if not content.isdigit():
        if on_failure:
            await on_failure(message, locale, progress + 1 if progress is not None else 0)
        else:
            await message.delete()
        return

    number = int(content)

    if number != progress + 1:
        if on_failure:
            await on_failure(message, locale, progress + 1)
        else:
            await message.delete()
        return

    if config is not None:
        last_counter_id = config.get("last_counter_id")
    else:
        last_counter_id = await get_last_counter_id_func(message.channel.id)

    if last_counter_id == str(message.author.id):
        if on_double_count:
            await on_double_count(message, locale, progress + 1)
        else:
            await message.delete()
        return

    await increase_progress_func(message.channel.id, message.author.id)
    # nosec: B311
    if random.randint(1, 100) == 1:
        await message.channel.send(str(progress + 2))
        await increase_progress_func(message.channel.id, "me")
