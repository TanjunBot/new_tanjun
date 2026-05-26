import asyncio
import logging

import discord

from api import (
    get_counting_challenge_progress,
    get_last_challenge_counter_id,
    increase_counting_challenge_progress,
    set_counting_challenge_progress,
)
from localizer import tanjunLocalizer
from minigames._counting_common import counting as _counting_base
from utility import tanjunEmbed

logger = logging.getLogger(__name__)


async def _challenge_failure(message: discord.Message, locale: str, _correct_number: int) -> None:
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "minigames.counting.failed.title"),
        description=tanjunLocalizer.localize(locale, "minigames.counting.failed.description"),
    )
    results = await asyncio.gather(
        message.add_reaction("\U0001f480"),
        message.reply(embed=embed),
        set_counting_challenge_progress(message.channel.id, 0),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            logger.warning("Error in counting challenge failure handler: %s", r)


async def _challenge_double_count(message: discord.Message, locale: str, _correct_number: int) -> None:
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "minigames.counting.failed_double.title"),
        description=tanjunLocalizer.localize(locale, "minigames.counting.failed_double.description"),
    )
    results = await asyncio.gather(
        message.add_reaction("\U0001f480"),
        message.reply(embed=embed),
        set_counting_challenge_progress(message.channel.id, 0),
        return_exceptions=True,
    )
    for r in results:
        if isinstance(r, Exception):
            logger.warning("Error in counting challenge double count handler: %s", r)


async def counting(message) -> None:
    await _counting_base(
        message,
        get_progress_func=get_counting_challenge_progress,
        get_last_counter_id_func=get_last_challenge_counter_id,
        increase_progress_func=increase_counting_challenge_progress,
        on_failure=_challenge_failure,
        on_double_count=_challenge_double_count,
    )
