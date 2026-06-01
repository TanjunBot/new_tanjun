from __future__ import annotations

from typing import Any


async def expect_interaction_or_modal(interaction: Any, _mocks: dict[str, Any]) -> None:
    if interaction.response.send_modal.await_count > 0:
        return
    await expect_interaction_response(interaction, _mocks)


async def expect_interaction_response(interaction: Any, _mocks: dict[str, Any]) -> None:
    if interaction.response.defer.await_count > 0:
        return
    if interaction.response.send_message.await_count > 0:
        return
    if interaction.followup.send.await_count > 0:
        return
    if interaction.response.send_modal.await_count > 0:
        return
    raise AssertionError("Expected defer, send_message, followup.send, or send_modal")


async def expect_defer(interaction: Any, _mocks: dict[str, Any]) -> None:
    if not interaction.response.defer.await_count:
        raise AssertionError("Expected interaction.response.defer to be awaited")


async def expect_mock_called(mock_name: str, mocks: dict[str, Any]) -> None:
    mock = mocks.get(mock_name)
    if mock is None:
        raise AssertionError(f"Mock {mock_name!r} not in mocks")
    if mock.await_count < 1 and mock.call_count < 1:
        raise AssertionError(f"Expected {mock_name!r} to be called")
