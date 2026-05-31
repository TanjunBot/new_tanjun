"""GitHub-related utilities: creating issues for missing localizations and feedback.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

from github import Github

from config import GithubAuthToken
from utils.async_io import run_blocking


async def missingLocalization(locale: str, key: str) -> None:  # noqa: N802
    """Create a GitHub issue reporting a missing localization."""
    await run_blocking(_sync_create_missing_localization_issue, locale, key)


def _sync_create_missing_localization_issue(locale: str, key: str) -> None:
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new_tanjun")
    label = repo.get_label("missing localization")
    repo.create_issue(
        title=f"Missing localization: {key} ({locale})",
        body=f"Missing translation for key `{key}` in locale `{locale}`.",
        labels=[label],
    )


async def addFeedback(content: str, author: str) -> None:  # noqa: N802
    """Create a GitHub issue with user feedback."""
    await run_blocking(_sync_create_feedback_issue, content, author)


def _sync_create_feedback_issue(content: str, author: str) -> None:
    g = Github(GithubAuthToken)
    repo = g.get_repo("TanjunBot/new_tanjun")
    label = repo.get_label("Feedback")
    repo.create_issue(
        title="Feedback",
        body=f"# {author} has given Feedback:\n{content}",
        labels=[label],
    )
