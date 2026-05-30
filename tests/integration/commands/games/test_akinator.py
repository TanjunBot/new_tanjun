"""Integration tests for commands.games.akinator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.games.akinator import akinator as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
@patch("commands.games.akinator.Akinator")
async def test_akinator_start(mock_aki_cls):
    mock_aki = MagicMock()
    mock_aki.start_game = MagicMock()
    mock_aki_cls.return_value = mock_aki
    info = make_command_info()
    await command_fn(info, None)
    embed_from_reply(info.reply)
