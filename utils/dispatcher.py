"""
Message handler dispatcher with priority-based execution ordering.

Extensions register their message handlers with a priority value;
critical handlers (e.g. counting) run before less urgent ones (e.g.
levels).  Handlers are dispatched in priority order, and a single
failing handler does not prevent others from running.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
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


async def dispatch(message: discord.Message) -> list[tuple[str, Any]]:
    """Run all registered handlers whose filters match *message*.

    Handlers are dispatched in priority order (lowest priority value
    first) and executed concurrently via ``asyncio.gather`` with
    ``return_exceptions=True`` so that a single failing handler does
    not prevent others from running.

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

    names: list[str] = [h.name for h in matched]
    coros: list[Awaitable[Any]] = [h.callback(message) for h in matched]

    log.debug("Dispatching %d handler(s) by priority: %s", len(matched), names)

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
