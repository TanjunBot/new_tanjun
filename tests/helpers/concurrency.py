from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


async def stress_concurrent(
    coro_factory: Callable[[], Awaitable[object]],
    n: int = 100,
) -> list[object]:
    return list(await asyncio.gather(*[coro_factory() for _ in range(n)]))
