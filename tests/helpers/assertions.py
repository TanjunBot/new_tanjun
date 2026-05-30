from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock


def _reply_mock(interaction: Any) -> AsyncMock | None:
    reply = getattr(interaction, "reply", None)
    return reply if isinstance(reply, AsyncMock) else None


def assert_reply_embed(interaction: Any, *, called: bool = True) -> None:
    reply = _reply_mock(interaction)
    assert reply is not None, "interaction has no reply mock"
    if called:
        reply.assert_awaited()
        assert "embed" in reply.await_args.kwargs
    else:
        reply.assert_not_awaited()


def assert_no_reply(interaction: Any) -> None:
    reply = _reply_mock(interaction)
    if reply is None:
        return
    assert reply.await_count == 0


def assert_command_responded(interaction: Any) -> None:
    reply = _reply_mock(interaction)
    if reply is not None and reply.await_count > 0:
        return
    response = getattr(interaction, "response", None)
    if response is not None:
        for attr in ("send_message", "defer", "send_modal", "edit_message"):
            method = getattr(response, attr, None)
            if isinstance(method, AsyncMock) and method.await_count > 0:
                return
    followup = getattr(interaction, "followup", None)
    if followup is not None:
        for attr in ("send", "send_message"):
            method = getattr(followup, attr, None)
            if isinstance(method, AsyncMock) and method.await_count > 0:
                return
    channel = getattr(interaction, "channel", None)
    if channel is not None:
        send = getattr(channel, "send", None)
        if isinstance(send, AsyncMock) and send.await_count > 0:
            return
    raise AssertionError("command did not produce a visible response")


def assert_matrix_outcome(info: Any, case: str, profile: Any, mocks: dict[str, Any] | None = None) -> None:
    from tests.helpers.command_profiles import ProfileKind

    mocks = mocks or {}
    if case == "no_guild" and profile.silent_no_guild:
        assert_no_reply(info)
        for mock in mocks.values():
            if isinstance(mock, AsyncMock):
                mock.assert_not_awaited()
        return
    if case == "restricted":
        assert_reply_embed(info)
        info.reply.assert_awaited_once()
        if profile.kind in (
            ProfileKind.BOOSTER_ADMIN,
            ProfileKind.COUNTING_MOD,
            ProfileKind.WORDCHAIN,
            ProfileKind.PERMISSION_HELPER,
        ):
            for mock in mocks.values():
                if isinstance(mock, AsyncMock):
                    mock.assert_not_awaited()
        return
    if case == "no_guild":
        assert_reply_embed(info)
        info.reply.assert_awaited_once()
        return
    if case == "admin":
        if profile.kind == ProfileKind.PERMISSION_HELPER:
            assert_no_reply(info)
            return
        if profile.kind == ProfileKind.WORDCHAIN:
            assert_reply_embed(info)
            info.reply.assert_awaited_once()
            channel = getattr(info, "channel", None)
            if channel is not None:
                send = getattr(channel, "send", None)
                if isinstance(send, AsyncMock) and send.await_count:
                    send.assert_awaited()
            return
        if profile.kind == ProfileKind.COUNTING_MOD:
            assert_reply_embed(info)
            info.reply.assert_awaited_once()
            if getattr(info.channel, "send", None) and info.channel.send.await_count:
                info.channel.send.assert_awaited()
            return
        if profile.kind == ProfileKind.BOOSTER_ADMIN:
            assert_reply_embed(info)
            info.reply.assert_awaited_once()
            if "add" in mocks and mocks["add"].await_count:
                mocks["add"].assert_awaited()
            elif "get" in mocks:
                mocks["get"].assert_awaited()
            return
        if profile.kind == ProfileKind.FEEDBACK_MODAL:
            assert_command_responded(info)
            return
        assert_command_responded(info)
        return
    raise AssertionError(f"unknown matrix case: {case}")
