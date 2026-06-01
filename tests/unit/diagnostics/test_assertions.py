from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from diagnostics.assertions import (
    expect_defer,
    expect_interaction_or_modal,
    expect_interaction_response,
    expect_mock_called,
)

pytestmark = pytest.mark.asyncio


def _interaction() -> MagicMock:
    ix = MagicMock()
    ix.response.defer = AsyncMock()
    ix.response.send_message = AsyncMock()
    ix.response.send_modal = AsyncMock()
    ix.followup.send = AsyncMock()
    ix.edit_original_response = AsyncMock()
    return ix


async def test_expect_interaction_response_send_message() -> None:
    ix = _interaction()
    await ix.response.send_message("hi")
    await expect_interaction_response(ix, {})


async def test_expect_interaction_response_raises() -> None:
    ix = _interaction()
    with pytest.raises(AssertionError, match="Expected defer"):
        await expect_interaction_response(ix, {})


async def test_expect_defer_ok() -> None:
    ix = _interaction()
    await ix.response.defer()
    await expect_defer(ix, {})


async def test_expect_interaction_or_modal_modal() -> None:
    ix = _interaction()
    await ix.response.send_modal(MagicMock())
    await expect_interaction_or_modal(ix, {})


async def test_expect_mock_called_ok() -> None:
    mock = AsyncMock()
    await mock()
    await expect_mock_called("svc", {"svc": mock})
