"""Centralized TTL cache with LRU eviction support.

Provides ``TTLCache``, an async-safe in-memory cache with
per-entry time-to-live and optional maximum-size LRU eviction.

Usage::

    from utils.cache import TTLCache

    # Simple TTL cache
    user_cache: TTLCache[str, UserModel] = TTLCache(ttl=120)
    item = user_cache.get("key")
    if item is None:
        item = await fetch_from_db()
        user_cache.set("key", item)

    # Bounded cache with LRU eviction (max 1000 entries)
    bounded: TTLCache[str, bytes] = TTLCache(ttl=60, maxsize=1000)
"""

from __future__ import annotations

import time
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class TTLCache(Generic[K, V]):
    """An in-memory cache with per-entry TTL and optional LRU eviction.

    Parameters
    ----------
    ttl : float
        Default time-to-live in seconds for each entry.
    maxsize : int, optional
        Maximum number of entries before LRU eviction kicks in.
        ``None`` (default) means unbounded.

    Thread-safety
    -------------
    This cache is **not** thread-safe by itself.  When used from
    async code with a single event-loop thread, access is naturally
    serialised.  For multi-threaded usage, wrap with ``asyncio.Lock``.
    """

    __slots__ = ("_ttl", "_maxsize", "_store", "_deadline")

    def __init__(self, ttl: float, maxsize: int | None = None) -> None:
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        if maxsize is not None and maxsize <= 0:
            raise ValueError("maxsize must be positive or None")
        self._ttl = ttl
        self._maxsize = maxsize
        # OrderedDict for O(1) LRU: move_to_end on get/set
        self._store: OrderedDict[K, V] = OrderedDict()
        self._deadline: dict[K, float] = {}

    # ── Public API ──────────────────────────────────────────────────────

    @property
    def ttl(self) -> float:
        """Return the default TTL for this cache."""
        return self._ttl

    @property
    def maxsize(self) -> int | None:
        """Return the maximum size, or ``None`` if unbounded."""
        return self._maxsize

    @property
    def size(self) -> int:
        """Return the current number of entries (including expired ones)."""
        self._evict_expired()
        return len(self._store)

    def get(self, key: K) -> V | None:
        """Retrieve a value, returning ``None`` if missing or expired."""
        deadline = self._deadline.get(key)
        if deadline is None:
            return None
        if time.monotonic() > deadline:
            self._discard(key)
            return None
        # LRU: move to end (most recently used)
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, key: K, value: V, *, ttl: float | None = None) -> None:
        """Store a value with the default or explicit TTL."""
        now = time.monotonic()
        self._store[key] = value
        self._deadline[key] = now + (ttl if ttl is not None else self._ttl)
        self._store.move_to_end(key)  # most recently used
        self._evict_lru()

    def delete(self, key: K) -> None:
        """Remove a single key if present; no-op otherwise."""
        self._discard(key)

    def invalidate(self, key: K) -> None:
        """Alias for :meth:`delete` — immediately expire *key*."""
        self.delete(key)

    def pop(self, key: K, default: V | None = None) -> V | None:
        """Remove *key* and return its value, or *default* if missing."""
        value = self.get(key)
        if value is None:
            return default
        self._discard(key)
        return value

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()
        self._deadline.clear()

    def contains(self, key: K) -> bool:
        """Check if *key* exists and is not expired (O(1))."""
        return self.get(key) is not None

    def keys(self) -> list[K]:
        """Return a snapshot of valid (non-expired) keys."""
        self._evict_expired()
        return list(self._store.keys())

    def values(self) -> list[V]:
        """Return a snapshot of valid (non-expired) values."""
        self._evict_expired()
        return list(self._store.values())

    def items(self) -> list[tuple[K, V]]:
        """Return a snapshot of valid (non-expired) key-value pairs."""
        self._evict_expired()
        return list(self._store.items())

    def get_or_compute(
        self,
        key: K,
        factory: Callable[[], V | Awaitable[V]],
        *,
        ttl: float | None = None,
    ) -> V | Awaitable[V]:
        """Return cached value or compute via *factory* (sync **or** async).

        If *factory* is a coroutine function, this returns an awaitable;
        otherwise returns the value directly.
        """
        existing = self.get(key)
        if existing is not None:
            return existing

        result = factory()
        if isinstance(result, Awaitable):
            return self._set_from_awaitable(key, result, ttl=ttl)
        self.set(key, result, ttl=ttl)
        return result

    async def _set_from_awaitable(self, key: K, awaitable: Awaitable[V], *, ttl: float | None) -> V:
        value = await awaitable
        self.set(key, value, ttl=ttl)
        return value

    def get_or_compute_sync(
        self,
        key: K,
        factory: Callable[[], V],
        *,
        ttl: float | None = None,
    ) -> V:
        """Synchronous variant of :meth:`get_or_compute` that does NOT await."""
        existing = self.get(key)
        if existing is not None:
            return existing
        value = factory()
        self.set(key, value, ttl=ttl)
        return value

    # ── Internal helpers ────────────────────────────────────────────────

    def _discard(self, key: K) -> None:
        self._store.pop(key, None)
        self._deadline.pop(key, None)

    def _evict_expired(self) -> None:
        now = time.monotonic()
        expired = [k for k, d in self._deadline.items() if now > d]
        for k in expired:
            self._discard(k)

    def _evict_lru(self) -> None:
        if self._maxsize is not None and len(self._store) > self._maxsize:
            # OrderedDict.popitem(last=False) removes the *first* (oldest) item
            oldest = self._store.popitem(last=False)
            self._deadline.pop(oldest[0], None)

    def __contains__(self, key: object) -> bool:
        """Check if *key* exists and is not expired."""
        try:
            return self.contains(key)  # type: ignore[arg-type]
        except TypeError:
            return False

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(ttl={self._ttl}, maxsize={self._maxsize}, size={self.size})"
