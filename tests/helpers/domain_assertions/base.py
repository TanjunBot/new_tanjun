from __future__ import annotations

import re
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from tests.helpers.command_matrix.models import MatrixCase

_ERROR_PATTERNS = (
    re.compile(r"invalid action", re.I),
    re.compile(r"err:\s*no translation", re.I),
)

_PERMISSION_FAILURE_PATTERNS = (
    re.compile(r"missing permissions?", re.I),
    re.compile(r"bot has missing permissions?", re.I),
    re.compile(r"permission denied", re.I),
    re.compile(r"not allowed to use this command", re.I),
    re.compile(r"you do not have the required permissions", re.I),
    re.compile(r"required permissions may be missing", re.I),
    re.compile(r"the bot does not have the required permissions", re.I),
    re.compile(r"the bot was unable to", re.I),
)

_DENIAL_TOKENS = (
    "permission",
    "denied",
    "not allowed",
    "missing",
    "cannot",
    "error",
    "required permissions",
    "moderate members",
    "administrator",
    "no emojis found",
    "no emotes found",
)


def _embed_from_content(content: str) -> Any:
    mock = MagicMock()
    mock.title = str(content)[:200]
    mock.description = str(content)
    mock.footer = None
    mock.fields = []
    return mock


def _embed_from_modal_or_view(value: Any) -> Any:
    mock = MagicMock()
    mock.title = getattr(value, "title", None) or type(value).__name__
    mock.description = type(value).__name__
    mock.footer = None
    mock.fields = []
    return mock


def embed_from_reply_or_response(reply: AsyncMock) -> Any:
    reply.assert_awaited()
    call = reply.await_args
    assert call is not None
    embed = call.kwargs.get("embed")
    if embed is not None:
        return embed
    content = call.kwargs.get("content")
    if content:
        return _embed_from_content(str(content))
    if call.args:
        first = call.args[0]
        if isinstance(first, str) and first.strip():
            return _embed_from_content(first)
        if first is not None and not isinstance(first, (int, float, bool)):
            type_name = type(first).__name__
            if "Modal" in type_name or "View" in type_name or hasattr(first, "children"):
                return _embed_from_modal_or_view(first)
    raise AssertionError("reply has no embed or content")


def embed_from_command_info(info: Any) -> Any:
    if info.reply.await_args_list or info.reply.call_args_list:
        return embed_from_reply_or_response(info.reply)
    interaction = getattr(info, "_matrix_interaction", None)
    if interaction is not None:
        response = interaction.response
        if getattr(response.send_modal, "called", False):
            modal = response.send_modal.call_args.args[0] if response.send_modal.call_args else None
            return _embed_from_modal_or_view(modal or "modal")
        if response.send_message.await_args_list:
            return embed_from_reply_or_response(response.send_message)
    raise AssertionError("command produced no embed, content, or modal response")


def embed_text(embed: Any) -> str:
    if isinstance(embed, dict):
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
    parts = [str(getattr(embed, "title", "") or ""), str(getattr(embed, "description", "") or "")]
    for field in getattr(embed, "fields", None) or []:
        parts.append(str(getattr(field, "name", "") or ""))
        parts.append(str(getattr(field, "value", "") or ""))
    footer = getattr(embed, "footer", None)
    if footer is not None:
        parts.append(str(getattr(footer, "text", "") or ""))
    return " ".join(parts)


def assert_no_error_markers(text: str, *, case_id: str) -> None:
    for pattern in _ERROR_PATTERNS:
        assert not pattern.search(text), f"error marker in response for {case_id}: {text!r}"


def is_permission_failure_text(text: str) -> bool:
    return any(pattern.search(text) for pattern in _PERMISSION_FAILURE_PATTERNS)


def live_response_text(result: dict[str, Any]) -> str:
    embed = result.get("embed")
    content = str(result.get("content") or "")
    if embed is not None:
        return embed_text(embed)
    return content


def assert_live_response_outcome(result: dict[str, Any], case: MatrixCase) -> bool:
    text = live_response_text(result)
    assert text.strip(), f"empty live response for {case.id}"
    assert_no_error_markers(text, case_id=case.id)
    if is_non_admin_permission(case) and is_denial_text(text):
        return True
    if case.dimension("permission", "admin") == "admin" and is_permission_failure_text(text):
        raise AssertionError(f"permission failure in live response for {case.id}: {text!r}")
    return False


def is_denial_text(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in _DENIAL_TOKENS)


def assert_permission_denial(embed: Any, case: MatrixCase) -> None:
    text = embed_text(embed)
    assert is_denial_text(text), f"expected permission denial for {case.id}: {text!r}"


_NON_ADMIN_PERMISSIONS = frozenset(
    {"restricted", "member", "no_guild", "channel_deny_send", "channel_deny_embed"}
)

_SUCCESS_HINT_TOKENS = (
    "success", "added", "removed", "updated", "enabled", "disabled", "set",
    "configured", "complete", "saved", "created", "deleted",
)


def is_non_admin_permission(case: MatrixCase) -> bool:
    return case.dimension("permission", "admin") in _NON_ADMIN_PERMISSIONS


def skip_if_denial(embed: Any, case: MatrixCase) -> bool:
    if not is_non_admin_permission(case):
        return False
    text = embed_text(embed)
    return is_denial_text(text)


def assert_default_embed(embed: Any, case: MatrixCase) -> None:
    text = embed_text(embed)
    assert text.strip(), f"empty embed for {case.id}"
    assert_no_error_markers(text, case_id=case.id)
