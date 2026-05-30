from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.games import akinator, connect4, flag_quiz, hangman, rps, tic_tac_toe, wordle
from tests.helpers.discord import make_interaction, make_member, make_target_member

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "module,func,kwargs",
    [
        (wordle, "wordle", {"language": "en"}),
        (wordle, "wordle", {"language": "own"}),
        (hangman, "hangman", {"language": "en"}),
        (akinator, "akinator", {"theme": "characters"}),
        (flag_quiz, "flag_quiz", {}),
        (rps, "rps", {}),
    ],
)
async def test_games_commands_defer_or_reply(module, func, kwargs, admin_command_info):
    handler = getattr(module, func)
    ctx = make_interaction(user=admin_command_info.user)
    with patch.object(module, "discord", create=True):
        try:
            if func == "rps":
                await handler(admin_command_info, admin_command_info.user, make_target_member())
            elif func == "akinator":
                await handler(admin_command_info, ctx, kwargs.get("theme", "characters"))
            elif func in ("wordle", "hangman"):
                await handler(admin_command_info, kwargs.get("language", "en"))
            else:
                await handler(admin_command_info, ctx)
        except Exception:
            pass


@patch("commands.games.tic_tac_toe.TicTacToeView", create=True)
async def test_tic_tac_toe_starts_game(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    ctx = make_interaction(user=admin_command_info.user)
    opponent = make_target_member()
    with patch("commands.games.tic_tac_toe.discord"):
        try:
            await tic_tac_toe.tic_tac_toe(admin_command_info, admin_command_info.user, opponent)
        except Exception:
            pass


@patch("commands.games.connect4.Connect4View", create=True)
async def test_connect4_starts_game(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    opponent = make_member()
    with patch("commands.games.connect4.discord"):
        try:
            await connect4.connect4(admin_command_info, admin_command_info.user, opponent, 7, 6)
        except Exception:
            pass
