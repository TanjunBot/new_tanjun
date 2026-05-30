"""Unit tests for tic-tac-toe game logic."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.tic_tac_toe import TicTacToe
from tests.helpers.discord import make_member


def _game(player2=None) -> TicTacToe:
    return TicTacToe(make_member(user_id=1), player2)


@pytest.mark.unit
class TestTicTacToeBoard:
    def test_initial_board_empty(self):
        game = _game()
        assert all(cell == "-" for row in game.board for cell in row)

    def test_check_winner_row(self):
        game = _game()
        game.board = [["⭕", "⭕", "⭕"], ["-", "-", "-"], ["-", "-", "-"]]
        assert game.check_winner() == "⭕"

    def test_check_winner_column(self):
        game = _game()
        game.board = [["❌", "-", "-"], ["❌", "-", "-"], ["❌", "-", "-"]]
        assert game.check_winner() == "❌"

    def test_check_winner_diagonal(self):
        game = _game()
        game.board = [["⭕", "-", "-"], ["-", "⭕", "-"], ["-", "-", "⭕"]]
        assert game.check_winner() == "⭕"

    def test_no_winner_empty_board(self):
        assert _game().check_winner() is None

    def test_is_full_false_on_empty(self):
        assert _game().is_full() is False

    def test_is_full_true_when_full(self):
        game = _game()
        game.board = [
            ["⭕", "❌", "⭕"],
            ["❌", "⭕", "❌"],
            ["❌", "⭕", "❌"],
        ]
        assert game.is_full() is True

    def test_get_available_moves_empty_board(self):
        game = _game()
        assert game.get_available_moves(game.board) == list(range(9))

    def test_minimax_make_move_places_symbol(self):
        game = _game()
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = game.minimax_make_move(board, 4, "⭕")
        assert new_board[1][1] == "⭕"

    def test_minimax_blocks_immediate_win(self):
        game = _game()
        board = [
            ["⭕", "⭕", "-"],
            ["-", "❌", "-"],
            ["-", "-", "-"],
        ]
        _, move = game.minimax("tanjun", 4, board, True)
        assert move == 2


@pytest.mark.unit
class TestTicTacToeHypothesis:
    @given(
        cells=st.lists(
            st.sampled_from(["-", "⭕", "❌"]),
            min_size=9,
            max_size=9,
        ),
    )
    @settings(max_examples=60)
    def test_check_winner_consistent_with_manual_scan(self, cells: list[str]):
        game = _game()
        game.board = [cells[i : i + 3] for i in range(0, 9, 3)]
        winner = game.check_winner()
        if winner is not None:
            assert winner in ("⭕", "❌")

    @given(move=st.integers(min_value=0, max_value=8))
    @settings(max_examples=20)
    def test_minimax_move_on_empty_board_in_range(self, move: int):
        game = _game()
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = game.minimax_make_move(board, move, "⭕")
        row, col = divmod(move, 3)
        assert new_board[row][col] == "⭕"
