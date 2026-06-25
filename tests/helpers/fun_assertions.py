from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

from tests.helpers.fun_matrix import FunMatrixCase


def embed_from_reply(reply: AsyncMock) -> Any:
    reply.assert_awaited()
    call = reply.await_args
    assert call is not None
    embed = call.kwargs.get("embed")
    assert embed is not None
    return embed


def assert_fun_embed_fields(
    embed: Any,
    case: FunMatrixCase,
    *,
    actor_name: str,
    target_name: str,
) -> None:
    title = str(getattr(embed, "title", "") or "")
    assert title, f"expected embed title for {case.id}"
    assert "Invalid action" not in title
    assert "err: no translation found" not in title
    assert actor_name.lower() in title.lower(), f"actor missing from title for {case.id}: {title!r}"
    assert target_name.lower() in title.lower(), f"target missing from title for {case.id}: {title!r}"

    footer = getattr(embed, "footer", None)
    footer_text = str(getattr(footer, "text", "") or "") if footer is not None else ""
    if footer_text:
        assert footer_text == "Powered By GIPHY"

    description = getattr(embed, "description", None)
    if case.message is not None and case.message != "":
        assert str(description or "") == case.message
    elif case.message_kind == "none":
        assert description in (None, "")


def assert_invalid_fun_embed(embed: Any) -> None:
    title = str(getattr(embed, "title", "") or "")
    assert title == "Invalid action"
