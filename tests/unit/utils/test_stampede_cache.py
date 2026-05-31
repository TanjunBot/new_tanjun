"""Tests for StampedeProtectedCache — prevents duplicate concurrent fetches."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable

import pytest

from utils.cache import StampedeProtectedCache


@pytest.mark.asyncio
async def test_get_or_fetch_single_call_on_concurrent_miss() -> None:
    cache: StampedeProtectedCache[str, int] = StampedeProtectedCache(ttl=60)
    calls = 0
    started = asyncio.Event()

    async def slow_fetch() -> int:
        nonlocal calls
        calls += 1
        started.set()
        await asyncio.sleep(0.05)
        return 42

    results = await asyncio.gather(*[cache.get_or_fetch("k", slow_fetch) for _ in range(50)])
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
    """Plain TTLCache has no per-key lock; concurrent misses may fetch multiple times."""
    from utils.cache import TTLCache

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
