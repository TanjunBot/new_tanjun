from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games import connect4, tic_tac_toe, wordle
from tests.helpers.assertions import assert_command_responded
from tests.helpers.discord import make_member, make_target_member


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_wordle_responds(admin_command_info):
    import io

    png = io.BytesIO(b"\x89PNG\r\n\x1a\n\xff")
    with (
        patch("commands.games.wordle.random.choice", return_value="about"),
        patch("commands.games.wordle.generate_wordle_image", AsyncMock(return_value=png)),
    ):
        await wordle.wordle(admin_command_info, "en")
    assert_command_responded(admin_command_info)


@patch("commands.games.tic_tac_toe.TicTacToeView", create=True)
async def test_tic_tac_toe_starts(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    with patch("commands.games.tic_tac_toe.discord"):
        await tic_tac_toe.tic_tac_toe(admin_command_info, admin_command_info.user, make_target_member())
    assert_command_responded(admin_command_info)


@patch("commands.games.connect4.Connect4View", create=True)
async def test_connect4_starts(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    with patch("commands.games.connect4.discord"):
        await connect4.connect4(admin_command_info, admin_command_info.user, make_member(), 7, 6)
    assert_command_responded(admin_command_info)
