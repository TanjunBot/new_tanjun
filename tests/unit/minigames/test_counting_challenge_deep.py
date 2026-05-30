from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from minigames import counting_challenge
from tests.helpers.discord import make_text_channel


pytestmark = pytest.mark.asyncio


def _message() -> MagicMock:
    msg = MagicMock()
    msg.channel = make_text_channel()
    return msg


@patch("minigames.counting_challenge._repo.set_progress", new_callable=AsyncMock)
@patch("minigames.counting_challenge.DiscordSafe.reply", new_callable=AsyncMock)
@patch("minigames.counting_challenge.DiscordSafe.add_reaction", new_callable=AsyncMock)
async def test_challenge_failure(mock_react, mock_reply, mock_set):
    await counting_challenge._challenge_failure(_message(), "en_US", 5)
    mock_react.assert_awaited_once()
    mock_reply.assert_awaited_once()
    mock_set.assert_awaited_once()


@patch("minigames.counting_challenge._repo.set_progress", new_callable=AsyncMock)
@patch("minigames.counting_challenge.DiscordSafe.reply", new_callable=AsyncMock)
@patch("minigames.counting_challenge.DiscordSafe.add_reaction", new_callable=AsyncMock)
async def test_challenge_double_count(mock_react, mock_reply, mock_set):
    await counting_challenge._challenge_double_count(_message(), "en_US", 5)
    mock_react.assert_awaited_once()
    mock_reply.assert_awaited_once()
    mock_set.assert_awaited_once()


@patch("minigames.counting_challenge._counting_base", new_callable=AsyncMock)
async def test_counting_delegates(mock_base):
    msg = _message()
    cfg = {"enabled": True}
    await counting_challenge.counting(msg, cfg)
    mock_base.assert_awaited_once()
    assert mock_base.await_args.kwargs["config"] is cfg
