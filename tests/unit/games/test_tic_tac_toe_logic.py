from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.tic_tac_toe import TicTacToe
from tests.helpers.discord import make_member, make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


def test_evaluate_board_player_wins():
    game = TicTacToe(make_member())
    board = [["⭕", "⭕", "⭕"], ["-", "-", "-"], ["-", "-", "-"]]
    assert game.evaluate_board(board) == -1


def test_evaluate_board_bot_wins():
    game = TicTacToe(make_member())
    board = [["❌", "❌", "❌"], ["-", "-", "-"], ["-", "-", "-"]]
    assert game.evaluate_board(board) == 1


def test_evaluate_board_draw():
    game = TicTacToe(make_member())
    board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
    assert game.evaluate_board(board) == 0


def test_get_available_moves():
    game = TicTacToe(make_member())
    board = [["⭕", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
    assert game.get_available_moves(board) == [1, 2, 3, 4, 5, 6, 7, 8]


def test_minimax_make_move():
    game = TicTacToe(make_member())
    board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
    new = game.minimax_make_move(board, 4, "⭕")
    assert new[1][1] == "⭕"


def test_toggle_turn_pvp():
    p1 = make_member(user_id=1)
    p2 = make_target_member(user_id=2)
    game = TicTacToe(p1, p2)
    game.toggle_turn()
    assert game.current_player is p2


pytestmark = pytest.mark.asyncio


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_view_play_move(mock_update):
    game = TicTacToe(make_member())
    game.player2 = "tanjun"
    game.current_player = game.player1
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(game.player1)
    interaction.response.defer = AsyncMock()
    interaction.message = MagicMock(id=1)
    button = MagicMock(custom_id="0")
    await view.play_0(interaction, button)
    mock_update.assert_awaited()


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_view_wrong_player(mock_update):
    game = TicTacToe(make_member())
    game.player2 = "tanjun"
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    wrong = make_view_interaction(make_target_member(user_id=999))
    wrong.response.defer = AsyncMock()
    wrong.followup = MagicMock()
    wrong.followup.send = AsyncMock()
    await view.play_0(wrong, MagicMock(custom_id="0"))
    wrong.followup.send.assert_awaited_once()


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_view_not_your_turn(mock_update):
    p1 = make_member(user_id=1)
    p2 = make_target_member(user_id=2)
    game = TicTacToe(p1, p2)
    game.current_player = p2
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(p1)
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    await view.play_0(interaction, MagicMock(custom_id="0"))
    interaction.followup.send.assert_awaited_once()


async def test_view_on_timeout():
    game = TicTacToe(make_member())
    msg = MagicMock()
    msg.edit = AsyncMock()
    view = game.getBoardView(message=msg, disable_on_timeout=True)
    await view.on_timeout()
    msg.edit.assert_awaited_once()
