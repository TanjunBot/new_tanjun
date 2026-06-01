"""GitHub-related utilities: creating issues for missing localizations and feedback.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

from __future__ import annotations

import hashlib
import logging
import time
import traceback
from typing import Any

import discord
from github import Github, GithubException

from config import GithubAuthToken, sentry_environment, version
from utils.async_io import run_blocking

logger = logging.getLogger(__name__)

_REPO = "TanjunBot/new_tanjun"
_EXCEPTION_LABELS = ("bug", "bot exception")
_DEDUP_TTL_SEC = 3600.0
_recent_reports: dict[str, float] = {}


def _is_discord_instance(exc: BaseException, exc_type: Any) -> bool:
    if not isinstance(exc_type, type):
        return False
    return isinstance(exc, exc_type)


def should_report_exception(exc: BaseException) -> bool:
    if _is_discord_instance(exc, discord.Forbidden):
        return False

    if _is_discord_instance(exc, discord.NotFound):
        return False

    if _is_discord_instance(exc, discord.HTTPException) and exc.status == 429:
        return False

    if _is_discord_instance(exc, discord.DiscordException):
        msg = str(exc).lower()
        if "10008" in msg and "unknown message" in msg:
            return False

    return True


def _exception_fingerprint(exc: BaseException) -> str:
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    location = ""
    for line in reversed(tb_lines):
        stripped = line.strip()
        if stripped.startswith('File "'):
            location = stripped
            break

    payload = f"{type(exc).__name__}:{exc!s}:{location}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _bot_exception_title_prefix(exc_name: str, source: str) -> str:
    return f"[Bot Exception] {exc_name} in {source}:"


def _open_bot_exception_issue_exists(
    g: Github,
    fingerprint: str,
    exc_name: str,
    source: str,
) -> bool:
    fingerprint_query = f'repo:{_REPO} is:issue is:open label:"bot exception" "{fingerprint}"'
    if g.search_issues(fingerprint_query).totalCount > 0:
        return True

    title_prefix = _bot_exception_title_prefix(exc_name, source)
    escaped_prefix = title_prefix.replace('"', '\\"')
    title_query = f'repo:{_REPO} is:issue is:open in:title "{escaped_prefix}"'
    return g.search_issues(title_query).totalCount > 0


def _dedup_allows_report(fingerprint: str) -> bool:
    now = time.monotonic()
    expired = [key for key, seen_at in _recent_reports.items() if now - seen_at >= _DEDUP_TTL_SEC]
    for key in expired:
        del _recent_reports[key]

    last_seen = _recent_reports.get(fingerprint)
    if last_seen is not None and now - last_seen < _DEDUP_TTL_SEC:
        return False

    _recent_reports[fingerprint] = now
    return True


def _format_context(context: dict[str, Any] | None) -> str:
    if not context:
        return "_No additional context._"

    lines = [f"- **{key}:** {value}" for key, value in context.items()]
    return "\n".join(lines)


def _resolve_labels(repo: Any) -> list[Any]:
    labels = []
    for label_name in _EXCEPTION_LABELS:
        try:
            labels.append(repo.get_label(label_name))
        except GithubException:
            continue
    return labels


def _sync_create_bot_exception_issue(
    exc: BaseException,
    *,
    source: str,
    context: dict[str, Any] | None = None,
) -> None:
    if not GithubAuthToken:
        return

    if not should_report_exception(exc):
        return

    fingerprint = _exception_fingerprint(exc)
    if not _dedup_allows_report(fingerprint):
        return

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    exc_name = type(exc).__name__
    exc_message = str(exc) or "(no message)"
    title = f"{_bot_exception_title_prefix(exc_name, source)} {exc_message}"
    if len(title) > 240:
        title = title[:237] + "..."

    environment = sentry_environment or "unknown"
    body = f"""## Bot Exception Report

**Fingerprint:** `{fingerprint}`
**Source:** `{source}`
**Exception:** `{exc_name}: {exc_message}`
**Version:** `{version}`
**Environment:** `{environment}`

### Context
{_format_context(context)}

### Traceback
```
{tb}
```
"""

    try:
        g = Github(GithubAuthToken)
        if _open_bot_exception_issue_exists(g, fingerprint, exc_name, source):
            return

        repo = g.get_repo(_REPO)
        labels = _resolve_labels(repo)
        repo.create_issue(title=title, body=body, labels=labels)
    except Exception as report_error:
        logger.error("Failed to create GitHub issue for bot exception: %s", report_error)


def report_bot_exception_sync(
    exc: BaseException,
    *,
    source: str = "unknown",
    context: dict[str, Any] | None = None,
) -> None:
    _sync_create_bot_exception_issue(exc, source=source, context=context)


async def report_bot_exception(
    exc: BaseException,
    *,
    source: str = "unknown",
    context: dict[str, Any] | None = None,
) -> None:
    await run_blocking(_sync_create_bot_exception_issue, exc, source=source, context=context)


async def missingLocalization(locale: str, key: str) -> None:  # noqa: N802
    """Create a GitHub issue reporting a missing localization."""
    await run_blocking(_sync_create_missing_localization_issue, locale, key)


def _missing_localization_issue_title(locale: str, key: str) -> str:
    return f"Missing localization: {key} ({locale})"


def _missing_localization_issue_exists(g: Github, locale: str, key: str) -> bool:
    title = _missing_localization_issue_title(locale, key)
    escaped_title = title.replace('"', '\\"')
    query = f'repo:{_REPO} is:issue in:title "{escaped_title}" state:open'
    return g.search_issues(query).totalCount > 0


def _sync_create_missing_localization_issue(locale: str, key: str) -> None:
    if not GithubAuthToken:
        return

    title = _missing_localization_issue_title(locale, key)

    try:
        g = Github(GithubAuthToken)
        if _missing_localization_issue_exists(g, locale, key):
            return

        repo = g.get_repo(_REPO)
        label = repo.get_label("missing localization")
        repo.create_issue(
            title=title,
            body=f"Missing translation for key `{key}` in locale `{locale}`.",
            labels=[label],
        )
    except Exception as report_error:
        logger.error("Failed to create missing localization issue: %s", report_error)


async def addFeedback(content: str, author: str) -> None:  # noqa: N802
    """Create a GitHub issue with user feedback."""
    await run_blocking(_sync_create_feedback_issue, content, author)


def _sync_create_feedback_issue(content: str, author: str) -> None:
    g = Github(GithubAuthToken)
    repo = g.get_repo(_REPO)
    label = repo.get_label("Feedback")
    repo.create_issue(
        title="Feedback",
        body=f"# {author} has given Feedback:\n{content}",
        labels=[label],
    )
