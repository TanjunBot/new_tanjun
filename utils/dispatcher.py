"""Message handler registry and dispatcher.

Provides a registry where extensions can register message handlers
with filter predicates (e.g., guild-only, ignore bots, channel
whitelist).  Once registered, all matching handlers can be dispatched
in one call, decoupling the core listener cog from individual features.
Handlers are executed with automatic exception isolation and structured
timing logs.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import discord

logger = logging.getLogger(__name__)

Handler = Callable[..., Awaitable[Any]]
"""Type alias for an async handler callable."""

CallbackType = Callable[..., Awaitable[None] | None]
"""Type alias for message handler callbacks (sync or async)."""


@dataclass
class MessageHandler:
    """A registered message handler with optional filter predicates.

    Attributes
    ----------
    name:
        Human-readable name for logging / debugging.
    callback:
        Callable (sync or async) that accepts ``(message, **kwargs)``.
    priority:
        Lower numbers run first.  Default is 100.
    only_guilds:
        If *True* (default), skip messages that are not in a guild.
    ignore_bots:
        If *True* (default), skip messages sent by bots.
    channel_whitelist:
        If set, only run for channels whose ID is in this set.
    kwargs:
        Additional keyword arguments forwarded to *callback* on dispatch.
    """

    name: str
    callback: CallbackType
    priority: int = 100
    only_guilds: bool = True
    ignore_bots: bool = True
    channel_whitelist: set[int] | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)


class HandlerRegistry:
    """Registry for message handlers with filter support.

    Extensions call ``register()`` to add their own handlers.  The
    core listener calls ``get_handlers(message)`` to retrieve the
    subset of handlers whose filters match the incoming message.
    """

    def __init__(self) -> None:
        self._handlers: list[MessageHandler] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, handler: MessageHandler) -> None:
        """Register a single handler.

        Parameters
        ----------
        handler:
            The handler to register.
        """
        self._handlers.append(handler)

    def register_multiple(self, handlers: list[MessageHandler]) -> None:
        """Register several handlers at once."""
        self._handlers.extend(handlers)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_handlers(self, message: discord.Message) -> list[MessageHandler]:
        """Return handlers whose filters match *message*, sorted by priority.

        Parameters
        ----------
        message:
            The incoming Discord message.

        Returns
        -------
            Sorted list of matching handlers.
        """
        matched: list[MessageHandler] = []
        for h in self._handlers:
            if not self._matches(h, message):
                continue
            matched.append(h)
        matched.sort(key=lambda h: h.priority)
        return matched

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _matches(handler: MessageHandler, message: discord.Message) -> bool:
        """Check whether *handler*'s filters pass for *message*."""
        if handler.ignore_bots and message.author.bot:
            return False
        if handler.only_guilds and message.guild is None:
            return False
        return not (handler.channel_whitelist is not None and message.channel.id not in handler.channel_whitelist)

    @property
    def count(self) -> int:
        """Number of registered handlers."""
        return len(self._handlers)


# ------------------------------------------------------------------
# Resilient execution helpers
# ------------------------------------------------------------------


async def _execute_with_logging(
    name: str,
    fn: Handler,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    message: discord.Message,
) -> Any:  # noqa: ANN401
    """Execute a handler with timing and exception logging.

    Parameters
    ----------
    name:
        Handler name for logging.
    fn:
        The async handler callable.
    args:
        Positional arguments to pass to the handler.
    kwargs:
        Keyword arguments to pass to the handler.
    message:
        The Discord message for context logging.

    Returns
    -------
        The handler result, or the ``Exception`` instance if it failed.
    """
    _t0 = time.monotonic()
    try:
        result = await fn(*args, **kwargs)
        _elapsed = (time.monotonic() - _t0) * 1000
        logger.debug(
            "Handler '%s' completed in %.1f ms for message %s",
            name,
            _elapsed,
            message.id,
        )
        return result
    except Exception as exc:
        _elapsed = (time.monotonic() - _t0) * 1000
        logger.exception(
            "Handler '%s' raised an exception after %.1f ms "
            "(message %s, channel %s): %s",
            name,
            _elapsed,
            message.id,
            message.channel.id,
            exc,
        )
        return exc


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

    async def _run_one(name: str, fn: Handler, *args: object, **kwargs: object) -> Any:  # noqa: ANN401
        return await _execute_with_logging(name, fn, args, kwargs, message)

    tasks = [
        _run_one(name, fn, *args, **kwargs)
        for name, fn, args, kwargs in handlers
    ]
    return await asyncio.gather(*tasks)


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
    results: list[Any] = []
    for name, fn, args, kwargs in handlers:
        result = await _execute_with_logging(name, fn, args, kwargs, message)
        results.append(result)
    return results


# ------------------------------------------------------------------
# Convenience decorator
# ------------------------------------------------------------------


def register_handler(
    name: str | None = None,
    *,
    priority: int = 100,
    only_guilds: bool = True,
    ignore_bots: bool = True,
    channel_whitelist: set[int] | None = None,
    **kwargs: object,
) -> Callable[[CallbackType], CallbackType]:
    """Decorator that registers a callable as a message handler.

    Example
    -------
    .. code:: python

        @register_handler("my_feature", priority=10)
        async def my_handler(message: discord.Message, **kw: Any) -> None:
            ...
    """

    def decorator(func: CallbackType) -> CallbackType:
        handler = MessageHandler(
            name=name or func.__name__,
            callback=func,
            priority=priority,
            only_guilds=only_guilds,
            ignore_bots=ignore_bots,
            channel_whitelist=channel_whitelist,
            kwargs=kwargs,
        )
        registry.register(handler)
        return func

    return decorator


# ------------------------------------------------------------------
# Module-level singleton – imported by listener cog and extensions
# ------------------------------------------------------------------
registry: HandlerRegistry = HandlerRegistry()
