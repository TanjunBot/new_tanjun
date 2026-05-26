from api import get_counting_progress, get_last_counter_id, increase_counting_progress
from minigames._counting_common import counting as _counting_base


async def counting(message, config: dict | None = None) -> None:
    """Normal counting handler. Accepts optional pre-fetched config to skip a DB query."""
    await _counting_base(
        message,
        get_progress_func=get_counting_progress,
        get_last_counter_id_func=get_last_counter_id,
        increase_progress_func=increase_counting_progress,
        config=config,
    )
