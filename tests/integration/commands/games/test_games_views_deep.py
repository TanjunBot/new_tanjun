from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games.connect4 import Connect4, connect4
from commands.games.rps import rps
from commands.games.tic_tac_toe import TicTacToe, tic_tac_toe
from tests.helpers.discord import make_member, make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


def test_connect4_diagonal_winner():
    game = Connect4(make_member(), locale="en")
    game.board[5][0] = game.player1_move
    game.board[4][1] = game.player1_move
    game.board[3][2] = game.player1_move
    game.board[2][3] = game.player1_move
    assert game.check_winner() == game.player1_move


def test_connect4_minimax_terminal():
    game = Connect4(make_member(), locale="en")
    game.board[5][0] = game.player2_move
    game.board[4][0] = game.player2_move
    game.board[3][0] = game.player2_move
    game.board[2][0] = game.player2_move
    score, move = game.minimax(game.player2_move, 2, game.board, True)
    assert score > 0


def test_tic_tac_toe_row_winner():
    game = TicTacToe(make_member(), make_member(user_id=2))
    for col in range(3):
        game.board[0][col] = game.player1_move
    assert game.check_winner() == game.player1_move


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_vs_bot(mock_update, admin_command_info):
    bot = make_target_member()
    bot.bot = True
    await connect4(admin_command_info, admin_command_info.user, bot)
    mock_update.assert_awaited()


@patch("commands.games.tic_tac_toe.TicTacToe.update_board", new_callable=AsyncMock)
async def test_tic_tac_toe_vs_member(mock_update, admin_command_info):
    await tic_tac_toe(admin_command_info, admin_command_info.user, make_target_member(user_id=222))
    mock_update.assert_awaited()


@patch("commands.games.rps.random.choice", return_value="paper")
async def test_rps_vs_bot_draw(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    rock = tanjunLocalizer.localize(locale, "commands.games.rps.rock")
    mock_choice.return_value = rock
    await rps(admin_command_info, None)
    admin_command_info.user.id = admin_command_info.user.id
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.rock(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice", return_value="scissors")
async def test_rps_vs_bot_win(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    rock = tanjunLocalizer.localize(locale, "commands.games.rps.rock")
    scissors = tanjunLocalizer.localize(locale, "commands.games.rps.scissors")
    mock_choice.return_value = scissors
    bot = make_target_member()
    bot.bot = True
    await rps(admin_command_info, bot)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.rock(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice")
async def test_rps_vs_bot_lose(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    rock = tanjunLocalizer.localize(locale, "commands.games.rps.rock")
    paper = tanjunLocalizer.localize(locale, "commands.games.rps.paper")
    mock_choice.return_value = paper
    await rps(admin_command_info, None)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.rock(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice")
async def test_rps_paper_vs_bot(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    paper = tanjunLocalizer.localize(locale, "commands.games.rps.paper")
    mock_choice.return_value = paper
    await rps(admin_command_info, None)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.paper(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


async def test_rps_pvp_second_player(admin_command_info):
    p2 = make_target_member(user_id=222222222)
    await rps(admin_command_info, p2)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.rock(interaction, MagicMock())
    interaction.message.edit.assert_awaited()
    p2_view = interaction.message.edit.await_args.kwargs.get("view")
    assert p2_view is not None
    p2_interaction = make_view_interaction(p2)
    p2_interaction.message = MagicMock(edit=AsyncMock())
    await p2_view.scissors(p2_interaction, MagicMock())
    p2_interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice")
async def test_rps_scissors_vs_bot(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    scissors = tanjunLocalizer.localize(locale, "commands.games.rps.scissors")
    mock_choice.return_value = scissors
    await rps(admin_command_info, None)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    await view.scissors(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice")
async def test_rps_paper_vs_bot(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    paper = tanjunLocalizer.localize(locale, "commands.games.rps.paper")
    rock = tanjunLocalizer.localize(locale, "commands.games.rps.rock")
    mock_choice.return_value = rock
    await rps(admin_command_info, None)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    interaction.response.defer = AsyncMock()
    await view.paper(interaction, MagicMock())
    interaction.message.edit.assert_awaited()


@patch("commands.games.rps.random.choice")
async def test_rps_scissors_pvp_second_player(mock_choice, admin_command_info):
    from localizer import tanjunLocalizer

    locale = admin_command_info.locale
    p2 = make_target_member(user_id=222222222)
    await rps(admin_command_info, p2)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    interaction.response.defer = AsyncMock()
    rock = tanjunLocalizer.localize(locale, "commands.games.rps.rock")
    await view.rock(interaction, MagicMock())
    p2_view = interaction.message.edit.await_args.kwargs.get("view")
    p2_interaction = make_view_interaction(p2)
    p2_interaction.message = MagicMock(edit=AsyncMock())
    p2_interaction.response.defer = AsyncMock()
    scissors = tanjunLocalizer.localize(locale, "commands.games.rps.scissors")
    await p2_view.scissors(p2_interaction, MagicMock())
    p2_interaction.message.edit.assert_awaited()


async def test_rps_wrong_player_ephemeral(admin_command_info):
    bot = make_target_member()
    bot.bot = True
    await rps(admin_command_info, bot)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup.send = AsyncMock()
    await view.rock(wrong, MagicMock())
    wrong.followup.send.assert_awaited_once()


async def test_rps_wrong_player_paper(admin_command_info):
    p2 = make_target_member(user_id=222222222)
    await rps(admin_command_info, p2)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup.send = AsyncMock()
    await view.paper(wrong, MagicMock())
    wrong.followup.send.assert_awaited_once()


async def test_rps_wrong_player_scissors(admin_command_info):
    p2 = make_target_member(user_id=222222222)
    await rps(admin_command_info, p2)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup.send = AsyncMock()
    await view.scissors(wrong, MagicMock())
    wrong.followup.send.assert_awaited_once()


async def _pvp_second_choice(admin_command_info, p1_method, p2_method):

    locale = admin_command_info.locale
    p2 = make_target_member(user_id=222222222)
    await rps(admin_command_info, p2)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(edit=AsyncMock())
    interaction.response.defer = AsyncMock()
    await p1_method(view, interaction)
    p2_view = interaction.message.edit.await_args.kwargs.get("view")
    p2_interaction = make_view_interaction(p2)
    p2_interaction.message = MagicMock(edit=AsyncMock())
    p2_interaction.response.defer = AsyncMock()
    await p2_method(p2_view, p2_interaction)
    p2_interaction.message.edit.assert_awaited()


async def test_rps_pvp_p2_rock(admin_command_info):
    await _pvp_second_choice(
        admin_command_info,
        lambda v, i: v.paper(i, MagicMock()),
        lambda v, i: v.rock(i, MagicMock()),
    )


async def test_rps_pvp_p2_paper(admin_command_info):
    await _pvp_second_choice(
        admin_command_info,
        lambda v, i: v.scissors(i, MagicMock()),
        lambda v, i: v.paper(i, MagicMock()),
    )


async def test_rps_pvp_p1_scissors(admin_command_info):
    await _pvp_second_choice(
        admin_command_info,
        lambda v, i: v.scissors(i, MagicMock()),
        lambda v, i: v.rock(i, MagicMock()),
    )


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_drop(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    game.player2 = "tanjun"
    game.current_player = game.player1
    msg = MagicMock()
    msg.edit = AsyncMock()
    view = game.getBoardView(message=msg)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    await view.drop(interaction, MagicMock())
    mock_update.assert_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_move_left(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    game.player2 = "tanjun"
    game.current_player = game.player1
    game.highlighted_column = game.available_columns()[1]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    await view.move_left(interaction, MagicMock())
    mock_update.assert_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_wrong_player(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    game.player2 = "tanjun"
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    wrong = make_view_interaction(make_target_member(user_id=99999))
    wrong.response.defer = AsyncMock()
    wrong.followup = MagicMock()
    wrong.followup.send = AsyncMock()
    await view.drop(wrong, MagicMock())
    wrong.followup.send.assert_awaited_once()
    mock_update.assert_not_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_drop_full_board(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    game.player2 = "tanjun"
    game.current_player = game.player1
    for col in range(game.columns):
        for row in range(game.rows):
            game.board[row][col] = game.player1_move if (row + col) % 2 == 0 else game.player2_move
    game.board[0][0] = game.empty_cell
    game.highlighted_column = 0
    interaction = make_view_interaction(admin_command_info.user)
    interaction.message = MagicMock(id=1)
    await game.drop(interaction)
    mock_update.assert_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_move_right(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    game.player2 = "tanjun"
    game.current_player = game.player1
    cols = game.available_columns()
    if len(cols) > 1:
        game.highlighted_column = cols[1]
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    await view.move_right(interaction, MagicMock())
    mock_update.assert_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_not_your_turn(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    p2 = make_target_member(user_id=2)
    game.player2 = p2
    game.current_player = p2
    view = game.getBoardView(message=MagicMock(edit=AsyncMock()))
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.defer = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    await view.drop(interaction, MagicMock())
    interaction.followup.send.assert_awaited_once()
    mock_update.assert_not_awaited()


@patch("commands.games.connect4.Connect4.update_board", new_callable=AsyncMock)
async def test_connect4_view_on_timeout(mock_update, admin_command_info):
    game = Connect4(admin_command_info.user, locale="en")
    msg = MagicMock()
    msg.edit = AsyncMock()
    view = game.getBoardView(message=msg)
    await view.on_timeout()
    msg.edit.assert_awaited_once()
