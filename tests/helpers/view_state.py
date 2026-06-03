from __future__ import annotations

import re
from typing import Any
from unittest.mock import AsyncMock


def _embed_description(embed: Any) -> str:
    if embed is None:
        return ""
    desc = getattr(embed, "description", None)
    if desc is not None:
        return str(desc)
    if hasattr(embed, "to_discord_embed"):
        converted = embed.to_discord_embed()
        return str(getattr(converted, "description", None) or "")
    return ""


def _embed_title(embed: Any) -> str:
    if embed is None:
        return ""
    title = getattr(embed, "title", None)
    if title is not None:
        return str(title)
    if hasattr(embed, "to_discord_embed"):
        converted = embed.to_discord_embed()
        return str(getattr(converted, "title", None) or "")
    return ""


def embed_from_reply(info: Any) -> Any:
    reply = getattr(info, "reply", None)
    assert isinstance(reply, AsyncMock) and reply.await_count > 0, "reply was not called"
    await_args = reply.await_args
    assert await_args is not None
    embed = await_args.kwargs.get("embed")
    assert embed is not None, "reply missing embed kwarg"
    return embed


def embed_from_edit(interaction: Any, *, call_index: int = -1) -> Any:
    response = getattr(interaction, "response", None)
    assert response is not None
    edit = getattr(response, "edit_message", None)
    assert isinstance(edit, AsyncMock) and edit.await_count > 0, "edit_message was not called"
    await_args = edit.await_args_list[call_index]
    embed = await_args.kwargs.get("embed")
    assert embed is not None, "edit_message missing embed kwarg"
    return embed


def embed_from_send(interaction: Any, *, call_index: int = -1) -> Any:
    response = getattr(interaction, "response", None)
    assert response is not None
    send = getattr(response, "send_message", None)
    assert isinstance(send, AsyncMock) and send.await_count > 0, "send_message was not called"
    await_args = send.await_args_list[call_index]
    embed = await_args.kwargs.get("embed")
    assert embed is not None, "send_message missing embed kwarg"
    return embed


def reply_description(info: Any) -> str:
    return _embed_description(embed_from_reply(info))


def edit_description(interaction: Any, *, call_index: int = -1) -> str:
    return _embed_description(embed_from_edit(interaction, call_index=call_index))


def assert_embed_page(embed: Any, page: int, total: int) -> None:
    desc = _embed_description(embed)
    assert f"Page {page}/{total}" in desc, f"expected Page {page}/{total} in description, got: {desc!r}"


def assert_embed_contains_keys(embed: Any, keys: list[str]) -> None:
    desc = _embed_description(embed)
    for key in keys:
        assert key in desc, f"expected {key!r} in embed description"


def assert_selection_marker(description: str, *, present: bool = True) -> None:
    if present:
        assert "➤" in description, "expected selection marker in description"
    else:
        assert "➤" not in description


def assert_embed_title_contains(embed: Any, text: str) -> None:
    assert text in _embed_title(embed), f"expected {text!r} in title, got {_embed_title(embed)!r}"


def count_selection_markers(description: str) -> int:
    return len(re.findall(r"➤", description))


def view_from_reply(info: Any) -> Any:
    reply = getattr(info, "reply", None)
    assert isinstance(reply, AsyncMock) and reply.await_count > 0
    view = reply.await_args.kwargs.get("view")
    assert view is not None, "reply missing view kwarg"
    return view
