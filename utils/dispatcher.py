"""
Message handler dispatcher with a registry for modular handler registration.

Extensions register their message handlers with filters; the dispatcher
runs only matching handlers and ensures resilience (one handler crash
does not prevent others from running).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

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
        if self.channel_blacklist is not None and message.channel.id in self.channel_blacklist:
            return False
        return True


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
    """Lower numbers run first. Use negative for early, positive for late."""


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

        @dispatcher.register(priority=-10)
        async def my_handler(message: discord.Message) -> None:
            ...

    Or as a direct call::

        dispatcher.register(my_handler, name="my_handler", priority=5)

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
        Lower numbers run first.
    """
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
# Dispatch
# ---------------------------------------------------------------------------


async def _invoke_handler(handler: MessageHandler, message: discord.Message) -> Any:  # noqa: ANN401
    """Invoke a single handler with timing instrumentation."""
    _t0 = time.monotonic()
    result = await handler.callback(message)
    _elapsed = (time.monotonic() - _t0) * 1000
    log.debug(
        "Handler '%s' completed in %.1f ms for message %s",
        handler.name,
        _elapsed,
        message.id,
    )
    return result


async def dispatch(message: discord.Message) -> list[tuple[str, Any]]:
    """Run all registered handlers whose filters match *message*.

    Handlers are executed concurrently via ``asyncio.gather`` with
    ``return_exceptions=True`` so that a single failing handler does not
    prevent others from running.

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

    names: list[str] = [h.name for h in matched]
    coros: list[Awaitable[Any]] = [_invoke_handler(h, message) for h in matched]

    log.debug("Dispatching %d handler(s): %s", len(matched), names)

    results = await asyncio.gather(*coros, return_exceptions=True)

    outcomes: list[tuple[str, Any]] = []
    for handler, result in zip(matched, results):
        outcomes.append((handler.name, result))
        if isinstance(result, Exception):
            log.exception(
                "Handler '%s' raised an exception for message %s in channel %s: %s",
                handler.name,
                message.id,
                message.channel.id,
                result,
                exc_info=result,
            )

    return outcomes


# ---------------------------------------------------------------------------
# Introspection / testing helpers
# ---------------------------------------------------------------------------


def registered_handlers() -> list[MessageHandler]:
    """Return a copy of the current handler registry (sorted by priority)."""
    return list(_handlers)


def clear() -> None:
    """Remove all registered handlers (useful for tests)."""
    _handlers.clear()


def freeze() -> None:
    """Mark registration as complete so no further handlers are expected."""
    global _ready
    _ready = True
    log.info("Dispatcher frozen with %d handler(s)", len(_handlers))
