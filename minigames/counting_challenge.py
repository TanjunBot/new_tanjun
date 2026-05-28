import discord

from localizer import tanjunLocalizer
from minigames._counting_common import counting as _counting_base
from services.counting_repository import CountingMode, CountingRepository
from utility import DiscordSafe, EmbedColor, tanjunEmbed

_repo = CountingRepository


async def _challenge_failure(message: discord.Message, locale: str, _correct_number: int) -> None:
    await DiscordSafe.add_reaction(message, "\U0001f480")
    embed = tanjunEmbed(
        colour=EmbedColor.ERROR,
        title=tanjunLocalizer.localize(locale, "minigames.counting.failed.title"),
        description=tanjunLocalizer.localize(locale, "minigames.counting.failed.description"),
    )
    await DiscordSafe.reply(message, embed=embed)
    await _repo.set_progress(CountingMode.CHALLENGE, message.channel.id, 0, 0)


async def _challenge_double_count(message: discord.Message, locale: str, _correct_number: int) -> None:
    await DiscordSafe.add_reaction(message, "\U0001f480")
    embed = tanjunEmbed(
        colour=EmbedColor.ERROR,
        title=tanjunLocalizer.localize(locale, "minigames.counting.failed_double.title"),
        description=tanjunLocalizer.localize(locale, "minigames.counting.failed_double.description"),
    )
    await DiscordSafe.reply(message, embed=embed)
    await _repo.set_progress(CountingMode.CHALLENGE, message.channel.id, 0, 0)


async def counting(message, config: dict | None = None) -> None:
    """Counting challenge handler. Accepts optional pre-fetched config to skip a DB query."""
    await _counting_base(
        message,
        get_progress_func=lambda cid: _repo.get_progress(CountingMode.CHALLENGE, cid),
        get_last_counter_id_func=lambda cid: _repo.get_last_counter_id(CountingMode.CHALLENGE, cid),
        increase_progress_func=lambda cid, uid: _repo.increment_progress(CountingMode.CHALLENGE, cid, uid),
        on_failure=_challenge_failure,
        on_double_count=_challenge_double_count,
        config=config,
    )
