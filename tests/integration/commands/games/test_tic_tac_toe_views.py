from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.tic_tac_toe import TicTacToe
from tests.helpers.discord import make_member, make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize("button_name,custom_id", [
    ("play_0", "0"),
    ("play_1", "1"),
    ("play_2", "2"),
    ("play_3", "3"),
    ("play_4", "4"),
    ("play_5", "5"),
    ("play_6", "6"),
    ("play_7", "7"),
    ("play_8", "8"),
])
@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_ttt_all_buttons(mock_update, button_name, custom_id):
    game = TicTacToe(make_member(), make_target_member(user_id=2))
    game.current_player = game.player1
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(game.player1)
    interaction.response.defer = AsyncMock()
    interaction.message = MagicMock(id=1)
    button = MagicMock(custom_id=custom_id)
    await getattr(view, button_name)(interaction, button)
    mock_update.assert_awaited()


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_ttt_pvp_second_player_move(mock_update):
    p1 = make_member(user_id=1)
    p2 = make_target_member(user_id=2)
    game = TicTacToe(p1, p2)
    game.current_player = p2
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(p2)
    interaction.response.defer = AsyncMock()
    interaction.message = MagicMock(id=1)
    await view.play_4(interaction, MagicMock(custom_id="4"))
    mock_update.assert_awaited()


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_ttt_bot_player_move(mock_update):
    game = TicTacToe(make_member())
    game.player2 = "tanjun"
    game.current_player = game.player1
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(game.player1)
    interaction.response.defer = AsyncMock()
    interaction.message = MagicMock(id=1)
    await view.play_0(interaction, MagicMock(custom_id="0"))
    mock_update.assert_awaited()


@pytest.mark.parametrize("button_name", [f"play_{i}" for i in range(9)])
async def test_ttt_wrong_player_all_buttons(button_name):
    p1 = make_member(user_id=1)
    p2 = make_target_member(user_id=2)
    game = TicTacToe(p1, p2)
    game.current_player = p1
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup.send = AsyncMock()
    await getattr(view, button_name)(wrong, MagicMock(custom_id=button_name.split("_")[1]))
    wrong.followup.send.assert_awaited_once()


@pytest.mark.parametrize("button_name", [f"play_{i}" for i in range(9)])
async def test_ttt_not_your_turn_all_buttons(button_name):
    p1 = make_member(user_id=1)
    p2 = make_target_member(user_id=2)
    game = TicTacToe(p1, p2)
    game.current_player = p2
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    wrong_turn = make_view_interaction(p1)
    wrong_turn.response.defer = AsyncMock()
    wrong_turn.followup.send = AsyncMock()
    await getattr(view, button_name)(wrong_turn, MagicMock(custom_id=button_name.split("_")[1]))
    wrong_turn.followup.send.assert_awaited_once()


async def test_ttt_view_on_timeout():
    msg = MagicMock()
    msg.edit = AsyncMock()
    game = TicTacToe(make_member(), make_target_member(user_id=2))
    view = game.getBoardView(message=msg)
    await view.on_timeout()
    msg.edit.assert_awaited_once()


async def test_ttt_update_board_winner():
    p1 = make_member(user_id=1)
    game = TicTacToe(p1)
    game.player2 = "tanjun"
    for col in range(3):
        game.board[0][col] = game.player1_move
    game.winner = game.player1_move
    interaction = make_view_interaction(p1)
    interaction.locale = "en_US"
    interaction.message = MagicMock(id=1)
    interaction.followup = MagicMock()
    interaction.followup.edit_message = AsyncMock()
    await game.update_board(interaction)
    interaction.followup.edit_message.assert_awaited_once()


async def test_ttt_update_board_draw():
    p1 = make_member(user_id=1)
    game = TicTacToe(p1, make_target_member(user_id=2))
    game.board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
    game.winner = None
    interaction = make_view_interaction(p1)
    interaction.locale = "en_US"
    interaction.message = MagicMock(id=1)
    interaction.followup = MagicMock()
    interaction.followup.edit_message = AsyncMock()
    await game.update_board(interaction)
    interaction.followup.edit_message.assert_awaited_once()
