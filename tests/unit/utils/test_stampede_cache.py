"""Tests for StampedeProtectedCache — prevents duplicate concurrent fetches."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from unittest.mock import patch

import pytest

from tests.helpers.concurrency import stress_concurrent
from utils.cache import StampedeProtectedCache, TTLCache


@pytest.mark.asyncio
async def test_get_or_fetch_single_call_on_concurrent_miss() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls = 0

    async def slow_fetch() -> int:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.05)
        return 42

    results = await stress_concurrent(lambda: cache.get_or_fetch("k", slow_fetch), n=50)
    assert all(r == 42 for r in results)
    assert calls == 1


@pytest.mark.asyncio
async def test_get_or_fetch_cache_hit_skips_fetch() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls = 0

    async def fetch() -> int:
        nonlocal calls
        calls += 1
        return 1

    assert await cache.get_or_fetch("a", fetch) == 1
    assert await cache.get_or_fetch("a", fetch) == 1
    assert calls == 1


@pytest.mark.asyncio
async def test_invalidate_forces_refetch() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls = 0

    async def fetch() -> int:
        nonlocal calls
        calls += 1
        return calls

    assert await cache.get_or_fetch("x", fetch) == 1
    cache.invalidate("x")
    assert await cache.get_or_fetch("x", fetch) == 2
    assert calls == 2


@pytest.mark.asyncio
async def test_plain_ttl_cache_get_or_compute_allows_duplicate_async_fetches() -> None:
    cache: TTLCache[str, int] = TTLCache(ttl=60)
    calls = 0

    async def factory() -> int:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.03)
        return 7

    async def run() -> int:
        result = cache.get_or_compute("k", factory)
        assert isinstance(result, Awaitable)
        return await result

    await asyncio.gather(*[run() for _ in range(10)])
    assert calls > 1


@pytest.mark.asyncio
async def test_ttl_expiry_forces_refetch() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=1)
    calls = 0
    t = 1000.0

    async def fetch() -> int:
        nonlocal calls
        calls += 1
        return calls

    with patch("utils.cache.time.monotonic", side_effect=lambda: t):
        assert await cache.get_or_fetch("k", fetch) == 1
    t += 2.0
    with patch("utils.cache.time.monotonic", side_effect=lambda: t):
        assert await cache.get_or_fetch("k", fetch) == 2
    assert calls == 2


@pytest.mark.asyncio
async def test_lru_eviction_at_maxsize() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60, maxsize=2)
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


@pytest.mark.asyncio
async def test_fetch_error_propagates_to_all_waiters() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    gate = asyncio.Event()

    async def failing_fetch() -> int:
        await gate.wait()
        raise RuntimeError("fetch failed")

    tasks = [asyncio.create_task(cache.get_or_fetch("k", failing_fetch)) for _ in range(10)]
    gate.set()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(r, RuntimeError) for r in results)
    assert cache.get("k") is None


@pytest.mark.asyncio
async def test_independent_keys_fetch_independently() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls: dict[str, int] = {"a": 0, "b": 0}

    async def fetch_a() -> int:
        calls["a"] += 1
        await asyncio.sleep(0.02)
        return 1

    async def fetch_b() -> int:
        calls["b"] += 1
        await asyncio.sleep(0.02)
        return 2

    await asyncio.gather(
        stress_concurrent(lambda: cache.get_or_fetch("a", fetch_a), n=20),
        stress_concurrent(lambda: cache.get_or_fetch("b", fetch_b), n=20),
    )
    assert calls["a"] == 1
    assert calls["b"] == 1


@pytest.mark.asyncio
async def test_caches_none_values() -> None:
    cache: StampedeProtectedCache[str, int | None] = StampedeProtectedCache(ttl=60)
    calls = 0

    async def fetch() -> None:
        nonlocal calls
        calls += 1
        return None

    assert await cache.get_or_fetch("k", fetch) is None
    assert await cache.get_or_fetch("k", fetch) is None
    assert calls == 1


@pytest.mark.asyncio
async def test_clear_during_in_flight_fetch() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    started = asyncio.Event()

    async def slow_fetch() -> int:
        started.set()
        await asyncio.sleep(0.05)
        return 99

    task = asyncio.create_task(cache.get_or_fetch("k", slow_fetch))
    await started.wait()
    cache.clear()
    assert await task == 99


@pytest.mark.asyncio
async def test_invalidate_during_in_flight_still_stores_fetched_value() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls = 0
    started = asyncio.Event()

    async def slow_fetch() -> int:
        nonlocal calls
        calls += 1
        started.set()
        await asyncio.sleep(0.05)
        return calls

    task = asyncio.create_task(cache.get_or_fetch("k", slow_fetch))
    await started.wait()
    cache.invalidate("k")
    assert await task == 1
    assert await cache.get_or_fetch("k", slow_fetch) == 1
    assert calls == 1
