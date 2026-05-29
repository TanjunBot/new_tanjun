"""Message dispatcher with resilience and structured logging.

Provides utilities for registering and dispatching message handlers
with automatic exception isolation and structured timing logs.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

import discord

logger = logging.getLogger(__name__)

Handler = Callable[..., Awaitable[Any]]
"""Type alias for an async handler callable."""


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
