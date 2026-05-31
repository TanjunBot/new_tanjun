from __future__ import annotations

import asyncio
import time

import pytest

from utils.async_io import run_blocking

pytestmark = pytest.mark.asyncio


def _blocking_add(a: int, b: int) -> int:
    return a + b


def _blocking_fail() -> None:
    raise ValueError("blocking error")


async def test_run_blocking_returns_result() -> None:
    result = await run_blocking(_blocking_add, 2, 3)
    assert result == 5


async def test_run_blocking_propagates_exception() -> None:
    with pytest.raises(ValueError, match="blocking error"):
        await run_blocking(_blocking_fail)


async def test_run_blocking_concurrent_calls_do_not_block_event_loop() -> None:
    def slow() -> int:
        time.sleep(0.05)
        return 1

    start = time.monotonic()
    results = await asyncio.gather(run_blocking(slow), run_blocking(slow), run_blocking(slow))
    elapsed = time.monotonic() - start
    assert results == [1, 1, 1]
    assert elapsed < 0.14
