"""Message handler registry and dispatcher.

Provides a registry where extensions can register message handlers
with filter predicates (e.g., guild-only, ignore bots, channel
whitelist).  Once registered, all matching handlers can be dispatched
in one call, decoupling the core listener cog from individual features.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

import discord

logger = logging.getLogger(__name__)


@dataclass
class MessageHandler:
    """A registered message handler with optional filter predicates.

    Attributes
    ----------
    name:
        Human-readable name for logging / debugging.
    callback:
        Async callable that accepts ``(message, **kwargs)``.
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
    callback: Any
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
) -> Callable[..., Awaitable[None]]:
    """Decorator that registers an async function as a message handler.

    Example
    -------
    .. code:: python

        @register_handler("my_feature", priority=10)
        async def my_handler(message: discord.Message, **kw: Any) -> None:
            ...
    """

    def decorator(func: Callable[..., Awaitable[None]]) -> Callable[..., Awaitable[None]]:
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
