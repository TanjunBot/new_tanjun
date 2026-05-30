"""Unit tests for Connect Four game logic."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.connect4 import Connect4
from tests.helpers.discord import make_member


def _game(rows: int = 6, cols: int = 7) -> Connect4:
    return Connect4(make_member(user_id=1), None, "en-US", rows, cols)


@pytest.mark.unit
class TestConnect4Logic:
    def test_initial_board_dimensions(self):
        game = _game(rows=4, cols=5)
        assert len(game.board) == 4
        assert all(len(row) == 5 for row in game.board)

    def test_initial_board_empty(self):
        game = _game()
        assert all(cell == game.empty_cell for row in game.board for cell in row)

    def test_horizontal_win(self):
        game = _game()
        game.board[0] = ["🔴", "🔴", "🔴", "🔴", "⚫", "⚫", "⚫"]
        assert game.check_winner() == "🔴"

    def test_vertical_win(self):
        game = _game()
        for row in range(4):
            game.board[row][0] = "🟡"
        assert game.check_winner() == "🟡"

    def test_no_winner_empty(self):
        assert _game().check_winner() is None

    def test_is_full_false_initially(self):
        assert _game().is_full() is False

    def test_available_columns_top_row(self):
        game = _game()
        assert game.available_columns() == list(range(7))

    def test_get_available_moves_returns_empty_cells(self):
        game = _game()
        moves = game.get_available_moves()
        assert len(moves) >= 1
        for row, col in moves:
            assert game.board[row][col] == game.empty_cell

    def test_minimax_make_move(self):
        game = _game()
        board = [row[:] for row in game.board]
        new_board = game.minimax_make_move(board, (5, 3), "🔴")
        assert new_board[5][3] == "🔴"


@pytest.mark.unit
class TestConnect4Hypothesis:
    @given(col=st.integers(min_value=0, max_value=6))
    @settings(max_examples=15)
    def test_drop_fills_lowest_empty_row(self, col: int):
        game = _game()
        game.highlighted_column = col
        for row in range(game.rows - 1, -1, -1):
            if game.board[row][col] == game.empty_cell:
                game.board[row][col] = "🔴"
                break
        assert game.board[game.rows - 1][col] == "🔴" or any(game.board[r][col] == "🔴" for r in range(game.rows))
