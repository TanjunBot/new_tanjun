"""Automatic GitHub issue creation for unhandled bot exceptions."""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any

from utils.github import report_bot_exception

logger = logging.getLogger(__name__)

_installed = False


class GitHubExceptionLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno < logging.ERROR or not record.exc_info:
            return

        _exc_type, exc_value, _tb = record.exc_info
        if exc_value is None:
            return

        context: dict[str, Any] = {
            "logger": record.name,
            "log_message": record.getMessage(),
        }
        _schedule_report(exc_value, source=f"logger:{record.name}", context=context)


def _schedule_report(
    exc: BaseException,
    *,
    source: str,
    context: dict[str, Any] | None = None,
) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        from utils.github import report_bot_exception_sync

        report_bot_exception_sync(exc, source=source, context=context)
        return

    loop.create_task(
        report_bot_exception(exc, source=source, context=context),
        name=f"github-report:{source}",
    )


def handle_asyncio_exception(loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
    exc = context.get("exception")
    if isinstance(exc, BaseException):
        report_context = {
            "asyncio_message": context.get("message"),
            "task": repr(context.get("task")),
        }
        _schedule_report(exc, source="asyncio", context=report_context)
        return

    message = context.get("message", "Unknown asyncio error")
    logger.error("Asyncio error without exception object: %s", message)


def handle_discord_event_error(event: str, *_args: Any, **_kwargs: Any) -> None:
    _exc_type, exc_value, _tb = sys.exc_info()
    if exc_value is None:
        return
    _schedule_report(exc_value, source=f"discord_event:{event}", context={"event": event})


def install_exception_reporter() -> None:
    global _installed
    if _installed:
        return

    root = logging.getLogger()
    root.addHandler(GitHubExceptionLogHandler())
    _installed = True
