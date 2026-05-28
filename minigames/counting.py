from services.counting_repository import CountingMode, CountingRepository


async def counting(message, config: dict | None = None) -> None:
    """Normal counting handler. Accepts optional pre-fetched config to skip a DB query."""
    repo = CountingRepository
    from minigames._counting_common import counting as _counting_base

    await _counting_base(
        message,
        get_progress_func=lambda cid: repo.get_progress(CountingMode.NORMAL, cid),
        get_last_counter_id_func=lambda cid: repo.get_last_counter_id(CountingMode.NORMAL, cid),
        increase_progress_func=lambda cid, uid: repo.increment_progress(CountingMode.NORMAL, cid, uid),
        config=config,
    )
