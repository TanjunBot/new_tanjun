from __future__ import annotations

from collections.abc import Iterator
from typing import Any, TypeVar
from unittest.mock import AsyncMock, MagicMock

T = TypeVar("T")


class AsyncIter:
    def __init__(self, items: list) -> None:
        self._items = list(reversed(items))

    def __aiter__(self) -> AsyncIter:
        return self

    async def __anext__(self) -> object:
        if not self._items:
            raise StopAsyncIteration
        return self._items.pop()


def make_mock_pool(
    fetchall: list | None = None,
    fetchone: tuple | None = None,
    rowcount: int = 0,
) -> tuple[Any, Any, Any]:
    cursor = AsyncMock(name="cursor")
    cursor.fetchall = AsyncMock(return_value=fetchall if fetchall is not None else [])
    cursor.fetchone = AsyncMock(return_value=fetchone)
    cursor.rowcount = rowcount
    cursor.execute = AsyncMock()
    cursor.__aiter__ = MagicMock(return_value=AsyncIter(fetchall or []))

    conn = MagicMock(name="conn")
    conn.cursor = MagicMock(return_value=AsyncMock())
    conn.cursor.return_value.__aenter__.return_value = cursor
    conn.__aenter__.return_value = conn
    conn.__aexit__.return_value = None
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()

    pool = MagicMock(name="pool")
    pool.acquire = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aenter__.return_value = conn

    return pool, conn, cursor


def make_bot(pool: object | None = None) -> tuple[MagicMock, object]:
    from api import set_bot

    if pool is None:
        pool, _, _ = make_mock_pool()
    bot = MagicMock(name="bot")
    bot._pool = pool
    set_bot(bot)
    return bot, pool


def reset_api_bot() -> Iterator[None]:
    from api import set_bot

    set_bot(None)
    yield
    set_bot(None)
