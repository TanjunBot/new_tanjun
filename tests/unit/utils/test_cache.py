"""Tests for utils/cache.py TTLCache."""

from __future__ import annotations

import time
from unittest.mock import patch

import pytest

from utils.cache import TTLCache


class TestTTLCacheInit:
    def test_valid_init(self):
        cache = TTLCache(ttl=60)
        assert cache.ttl == 60
        assert cache.maxsize is None

    def test_invalid_ttl_raises(self):
        with pytest.raises(ValueError, match="ttl must be positive"):
            TTLCache(ttl=0)

    def test_invalid_maxsize_raises(self):
        with pytest.raises(ValueError, match="maxsize must be positive"):
            TTLCache(ttl=60, maxsize=0)


class TestTTLCacheBasicOps:
    def test_set_and_get(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value")
        assert cache.get("key") == "value"

    def test_get_missing_returns_none(self):
        cache = TTLCache(ttl=60)
        assert cache.get("missing") is None

    def test_delete(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value")
        cache.delete("key")
        assert cache.get("key") is None

    def test_invalidate_alias(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value")
        cache.invalidate("key")
        assert cache.get("key") is None

    def test_pop(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value")
        assert cache.pop("key") == "value"
        assert cache.get("key") is None

    def test_pop_default(self):
        cache = TTLCache(ttl=60)
        assert cache.pop("missing", "default") == "default"

    def test_clear(self):
        cache = TTLCache(ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.size == 0

    def test_contains(self):
        cache = TTLCache(ttl=60)
        cache.set("key", 1)
        assert "key" in cache
        assert "missing" not in cache

    def test_len(self):
        cache = TTLCache(ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        assert len(cache) == 2


class TestTTLCacheExpiry:
    def test_expired_entry_returns_none(self):
        cache = TTLCache(ttl=0.01)
        cache.set("key", "value")
        time.sleep(0.02)
        assert cache.get("key") is None

    def test_custom_ttl_on_set(self):
        cache = TTLCache(ttl=60)
        cache.set("key", "value", ttl=0.01)
        time.sleep(0.02)
        assert cache.get("key") is None


class TestTTLCacheLRU:
    def test_evicts_oldest_when_maxsize_exceeded(self):
        cache = TTLCache(ttl=60, maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_get_updates_lru_order(self):
        cache = TTLCache(ttl=60, maxsize=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.get("a")
        cache.set("c", 3)
        assert cache.get("a") == 1
        assert cache.get("b") is None


class TestTTLCacheSnapshots:
    def test_keys_values_items(self):
        cache = TTLCache(ttl=60)
        cache.set("a", 1)
        cache.set("b", 2)
        assert set(cache.keys()) == {"a", "b"}
        assert set(cache.values()) == {1, 2}
        assert dict(cache.items()) == {"a": 1, "b": 2}


class TestTTLCacheCompute:
    def test_get_or_compute_sync(self):
        cache = TTLCache(ttl=60)
        calls = []

        def factory():
            calls.append(1)
            return 42

        assert cache.get_or_compute_sync("key", factory) == 42
        assert cache.get_or_compute_sync("key", factory) == 42
        assert len(calls) == 1

    @pytest.mark.asyncio
    async def test_get_or_compute_async(self):
        cache = TTLCache(ttl=60)
        calls = []

        async def factory():
            calls.append(1)
            return 99

        result = cache.get_or_compute("key", factory)
        value = await result
        assert value == 99
        assert cache.get("key") == 99
        assert len(calls) == 1

    def test_repr(self):
        cache = TTLCache(ttl=60, maxsize=10)
        assert "TTLCache" in repr(cache)
