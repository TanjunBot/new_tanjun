"""Message handler dispatcher with priority-based execution ordering.

Extensions register their message handlers with a priority value;
critical handlers (e.g. counting) run before less urgent ones (e.g.
levels).  Handlers are dispatched in priority order, and a single
failing handler does not prevent others from running.

Provides automatic exception isolation and structured timing logs.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import discord

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Filter types
# ---------------------------------------------------------------------------


@dataclass
class MessageFilters:
    """Constraints a message must satisfy for the handler to run."""

    only_guilds: bool = True
    """If True, skip DMs (message.guild must be set)."""

    ignore_bots: bool = True
    """If True, skip messages from bots."""

    channel_whitelist: set[int] | None = None
    """If set, only run in these channel IDs (None = allow all)."""

    channel_blacklist: set[int] | None = None
    """If set, never run in these channel IDs."""

    def check(self, message: discord.Message) -> bool:
        """Return True if *message* passes all configured filters."""
        if self.ignore_bots and message.author.bot:
            return False
        if self.only_guilds and message.guild is None:
            return False
        if self.channel_whitelist is not None and message.channel.id not in self.channel_whitelist:
            return False
        return not (self.channel_blacklist is not None and message.channel.id in self.channel_blacklist)


# ---------------------------------------------------------------------------
# Priority constants
# ---------------------------------------------------------------------------


class Priority:
    """Convenience constants for common priority tiers.

    Use these to keep priority values consistent across handlers::

        @dispatcher.register(priority=Priority.CRITICAL)
        async def counting_handler(message: discord.Message) -> None: ...
    """

    CRITICAL: int = -100
    """For handlers that must run before anything else (e.g. counting)."""

    HIGH: int = -50
    """For important handlers that should run early."""

    NORMAL: int = 0
    """Default priority for most handlers."""

    LOW: int = 50
    """For handlers that can wait (e.g. leveling, stats)."""

    BACKGROUND: int = 100
    """For non-urgent background processing."""


# ---------------------------------------------------------------------------
# Handler record
# ---------------------------------------------------------------------------


@dataclass
class MessageHandler:
    """A registered message handler with its metadata."""

    name: str
    """Human-readable name (used in logs)."""

    callback: Callable[[discord.Message], Awaitable[Any]]
    """Async callable that processes the message."""

    filters: MessageFilters = field(default_factory=MessageFilters)
    """Filters that gate execution."""

    priority: int = 0
    """Lower numbers run first. Use :class:`Priority` constants."""


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------

_handlers: list[MessageHandler] = []
"""Global list of registered handlers (sorted by priority on registration)."""

_ready: bool = False
"""Set True after all extensions are loaded and no more handlers are expected."""


def register(
    callback: Callable[[discord.Message], Awaitable[Any]] | None = None,
    *,
    name: str | None = None,
    filters: MessageFilters | None = None,
    priority: int = 0,
) -> Callable[[Callable[[discord.Message], Awaitable[Any]]], Callable[[discord.Message], Awaitable[Any]]]:
    """Register a message handler.

    Can be used as a decorator::

        @dispatcher.register(priority=Priority.CRITICAL)
        async def my_handler(message: discord.Message) -> None:
            ...

    Or as a direct call::

        dispatcher.register(my_handler, name="my_handler", priority=Priority.LOW)

    Parameters
    ----------
    callback:
        The async handler function.  If omitted the return value is a
        decorator.
    name:
        Display name for logs (defaults to ``callback.__name__``).
    filters:
        :class:`MessageFilters` instance.  Falls back to defaults.
    priority:
        Lower numbers run first.  Use :class:`Priority` constants.
    """
    if _ready:
        raise RuntimeError("Cannot register message handlers after dispatcher.freeze()")

    if callback is None:
        # Decorator form
        def _decorator(
            fn: Callable[[discord.Message], Awaitable[Any]],
        ) -> Callable[[discord.Message], Awaitable[Any]]:
            register(fn, name=name or fn.__name__, filters=filters, priority=priority)
            return fn

        return _decorator

    handler_name = name or callback.__name__
    handler = MessageHandler(
        name=handler_name,
        callback=callback,
        filters=filters or MessageFilters(),
        priority=priority,
    )
    _handlers.append(handler)
    _handlers.sort(key=lambda h: h.priority)
    log.debug("Registered message handler '%s' (priority=%d)", handler_name, priority)
    return callback


# ---------------------------------------------------------------------------
# Resilient execution with timing
# ---------------------------------------------------------------------------

Handler = Callable[..., Awaitable[Any]]
"""Type alias for an async handler callable."""


async def _execute_with_logging(
    name: str,
    fn: Callable[[discord.Message], Awaitable[Any]],
    message: discord.Message,
) -> Any:  # noqa: ANN401
    """Execute a handler with timing and exception logging.

    Parameters
    ----------
    name:
        Handler name for logging.
    fn:
        The async handler callable.
    message:
        The Discord message for context logging.

    Returns
    -------
        The handler result, or the ``Exception`` instance if it failed.
    """
    _t0 = time.monotonic()
    try:
        result = await fn(message)
        _elapsed = (time.monotonic() - _t0) * 1000
        log.debug(
            "Handler '%s' completed in %.1f ms for message %s",
            name,
            _elapsed,
            message.id,
        )
        return result
    except Exception as exc:
        _elapsed = (time.monotonic() - _t0) * 1000
        log.exception(
            "Handler '%s' raised an exception after %.1f ms (message %s, channel %s): %s",
            name,
            _elapsed,
            message.id,
            message.channel.id,
            exc,
        )
        return exc


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


async def dispatch(message: discord.Message) -> list[tuple[str, Any]]:
    """Run all registered handlers whose filters match *message*.

    Handlers are dispatched in priority order (lowest priority value
    first) and executed concurrently via ``asyncio.gather`` with
    exception isolation so that a single failing handler does not
    prevent others from running.

    Each handler execution is timed and logged for observability.

    Parameters
    ----------
    message:
        The incoming Discord message.

    Returns
    -------
    list[(name, result)]
        A list of ``(handler_name, return_value_or_exception)`` tuples
        for every handler that was executed.
    """
    matched: list[MessageHandler] = []
    for handler in _handlers:
        try:
            if handler.filters.check(message):
                matched.append(handler)
        except Exception:
            log.exception("Filter check failed for handler '%s'", handler.name)

    if not matched:
        return []

    from itertools import groupby

    outcomes: list[tuple[str, Any]] = []
    for _, batch_iter in groupby(matched, key=lambda h: h.priority):
        batch = list(batch_iter)
        names: list[str] = [h.name for h in batch]
        log.debug("Dispatching %d handler(s) at priority %d: %s", len(batch), batch[0].priority, names)

        coros: list[Awaitable[Any]] = [_execute_with_logging(h.name, h.callback, message) for h in batch]
        results = await asyncio.gather(*coros, return_exceptions=True)

        for handler, result in zip(batch, results, strict=True):
            outcomes.append((handler.name, result))

    return outcomes


# ---------------------------------------------------------------------------
# Utility execution modes
# ---------------------------------------------------------------------------


async def run_handlers_safe(
    handlers: list[tuple[str, Handler, tuple[Any, ...], dict[str, Any]]],
    message: discord.Message,
) -> list[Any]:
    """Run multiple handlers concurrently with exception isolation and logging.

    Each handler runs as an independent task so that a crash in one does
    not affect the others.  Handlers are logged with timing info and
    any exceptions are captured and logged at error level.

    Parameters
    ----------
    handlers:
        List of ``(name, callable, args, kwargs)`` tuples.
    message:
        The Discord message that triggered these handlers (used for context).

    Returns
    -------
        Results from each handler (may include ``Exception`` instances).
    """

    async def _execute_generic(
        name: str,
        fn: Handler,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        _t0 = time.monotonic()
        try:
            result = await fn(*args, **kwargs)
            _elapsed = (time.monotonic() - _t0) * 1000
            log.debug(
                "Handler '%s' completed in %.1f ms for message %s",
                name,
                _elapsed,
                message.id,
            )
            return result
        except Exception as exc:
            _elapsed = (time.monotonic() - _t0) * 1000
            log.exception(
                "Handler '%s' raised an exception after %.1f ms (message %s, channel %s): %s",
                name,
                _elapsed,
                message.id,
                message.channel.id,
                exc,
            )
            return exc

    tasks = [_execute_generic(name, fn, args, kwargs) for name, fn, args, kwargs in handlers]
    return await asyncio.gather(*tasks, return_exceptions=True)


async def run_handlers_sequential(
    handlers: list[tuple[str, Handler, tuple[Any, ...], dict[str, Any]]],
    message: discord.Message,
) -> list[Any]:
    """Run handlers sequentially with exception isolation and logging.

    Each handler runs in order.  If one fails, subsequent handlers
    still run.  Exceptions are caught and logged; an ``Exception``
    instance is returned in place of the normal result.

    Parameters
    ----------
    handlers:
        List of ``(name, callable, args, kwargs)`` tuples.
    message:
        The Discord message that triggered these handlers (used for context).

    Returns
    -------
        Results from each handler (may include ``Exception`` instances).
    """

    async def _execute_generic(
        name: str,
        fn: Handler,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> Any:  # noqa: ANN401
        _t0 = time.monotonic()
        try:
            result = await fn(*args, **kwargs)
            _elapsed = (time.monotonic() - _t0) * 1000
            log.debug(
                "Handler '%s' completed in %.1f ms for message %s",
                name,
                _elapsed,
                message.id,
            )
            return result
        except Exception as exc:
            _elapsed = (time.monotonic() - _t0) * 1000
            log.exception(
                "Handler '%s' raised an exception after %.1f ms (message %s, channel %s): %s",
                name,
                _elapsed,
                message.id,
                message.channel.id,
                exc,
            )
            return exc

    results: list[Any] = []
    for name, fn, args, kwargs in handlers:
        result = await _execute_generic(name, fn, args, kwargs)
        results.append(result)
    return results


# ---------------------------------------------------------------------------
# Introspection / testing helpers
# ---------------------------------------------------------------------------


def registered_handlers() -> list[MessageHandler]:
    """Return a copy of the current handler registry (sorted by priority)."""
    return list(_handlers)


def clear() -> None:
    """Remove all registered handlers (useful for tests)."""
    global _ready
    _handlers.clear()
    _ready = False
    log.debug("Dispatcher cleared")


def freeze() -> None:
    """Mark registration as complete so no further handlers are expected."""
    global _ready
    _ready = True
    log.info("Dispatcher frozen with %d handler(s)", len(_handlers))
