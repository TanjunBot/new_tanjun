from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Callable

from tests.helpers.live_e2e.models import BotResponse, CommandLiveCase

if TYPE_CHECKING:
    from tests.helpers.live_discord.session import LiveGuildSession

_ERROR_PATTERNS = (
    re.compile(r"invalid action", re.I),
    re.compile(r"err:\s*no translation", re.I),
    re.compile(r"permission denied", re.I),
    re.compile(r"missing permissions", re.I),
    re.compile(r"you don't have permission", re.I),
)


def _embed_text(embed: dict[str, Any]) -> str:
    parts = [
        str(embed.get("title") or ""),
        str(embed.get("description") or ""),
    ]
    for field in embed.get("fields") or []:
        parts.append(str(field.get("name") or ""))
        parts.append(str(field.get("value") or ""))
    footer = embed.get("footer") or {}
    parts.append(str(footer.get("text") or ""))
    return " ".join(parts)


def _assert_no_error_markers(text: str, *, case_id: str) -> None:
    for pattern in _ERROR_PATTERNS:
        assert not pattern.search(text), f"error marker in response for {case_id}: {text!r}"


def assert_default(response: BotResponse, case: CommandLiveCase, *, session: LiveGuildSession) -> None:
    del session
    if case.response_kind == "embed":
        assert response.embed is not None, f"expected embed for {case.id}"
        text = _embed_text(response.embed)
        assert text.strip(), f"empty embed for {case.id}"
        _assert_no_error_markers(text, case_id=case.id)
    elif case.response_kind == "message":
        assert response.content and response.content.strip(), f"expected message for {case.id}"
        _assert_no_error_markers(response.content, case_id=case.id)
    else:
        has_embed = response.embed is not None and _embed_text(response.embed).strip()
        has_content = bool(response.content and response.content.strip())
        assert has_embed or has_content, f"expected embed or message for {case.id}"
        text = _embed_text(response.embed) if response.embed else (response.content or "")
        _assert_no_error_markers(text, case_id=case.id)
    for substring in case.expected_substrings:
        haystack = _embed_text(response.embed) if response.embed else (response.content or "")
        assert substring.lower() in haystack.lower(), (
            f"expected {substring!r} in response for {case.id}: {haystack!r}"
        )


def assert_math(response: BotResponse, case: CommandLiveCase, *, session: LiveGuildSession) -> None:
    del session
    assert_default(response, case, session=session)
    if "calc" in case.tree_path or "calculator" in case.tree_path:
        haystack = _embed_text(response.embed) if response.embed else (response.content or "")
        assert "4" in haystack or "2+2" in haystack.lower(), f"unexpected calc result for {case.id}"


def assert_games(response: BotResponse, case: CommandLiveCase, *, session: LiveGuildSession) -> None:
    assert_default(response, case, session=session)


def assert_ai(response: BotResponse, case: CommandLiveCase, *, session: LiveGuildSession) -> None:
    assert_default(response, case, session=session)


ASSERT_PROFILES: dict[str, Callable[..., None]] = {
    "default": assert_default,
    "math": assert_math,
    "games": assert_games,
    "ai": assert_ai,
}


def assert_command_response(
    result: dict[str, Any] | BotResponse,
    case: CommandLiveCase,
    *,
    session: LiveGuildSession,
) -> None:
    if isinstance(result, dict):
        response = BotResponse(
            embed=result.get("embed"),
            content=result.get("content"),
            message=result.get("message"),
        )
    else:
        response = result
    profile = ASSERT_PROFILES.get(case.assert_profile, assert_default)
    profile(response, case, session=session)
