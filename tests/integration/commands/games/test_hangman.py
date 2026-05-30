"""Integration tests for commands.games.hangman."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from commands.games.hangman import hangman as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
@patch("commands.games.hangman.random.choice")
async def test_hangman_start(mock_choice):
    mock_choice.return_value = "test"
    info = make_command_info()
    await command_fn(info, "en")
    embed_from_reply(info.reply)
