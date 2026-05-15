"""Tests for TicTacToe and Connect4 pure game logic — comprehensive."""
import pytest

from tests.mock_config import patch_config_module

patch_config_module()

from commands.games.tic_tac_toe import TicTacToe
from commands.games.connect4 import Connect4


# ==================== TicTacToe ====================


class TestTicTacToeCheckWinner:
    def test_empty_board_no_winner(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.check_winner()
        assert result is None

    def test_row_win_first_row(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "⭕", "⭕"], ["-", "-", "-"], ["-", "-", "-"]]
        ttt.player1_move = "⭕"
        result = ttt.check_winner()
        assert result == "⭕"

    def test_row_win_second_row(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["❌", "❌", "❌"], ["-", "-", "-"]]
        ttt.player2_move = "❌"
        result = ttt.check_winner()
        assert result == "❌"

    def test_row_win_third_row(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["-", "-", "-"], ["⭕", "⭕", "⭕"]]
        result = ttt.check_winner()
        assert result == "⭕"

    def test_col_win_first_col(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "-", "-"], ["⭕", "-", "-"], ["⭕", "-", "-"]]
        result = ttt.check_winner()
        assert result == "⭕"

    def test_col_win_second_col(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "❌", "-"], ["-", "❌", "-"], ["-", "❌", "-"]]
        result = ttt.check_winner()
        assert result == "❌"

    def test_col_win_third_col(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "⭕"], ["-", "-", "⭕"], ["-", "-", "⭕"]]
        result = ttt.check_winner()
        assert result == "⭕"

    def test_diagonal_top_left_to_bottom_right(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "-", "-"], ["-", "⭕", "-"], ["-", "-", "⭕"]]
        result = ttt.check_winner()
        assert result == "⭕"

    def test_diagonal_top_right_to_bottom_left(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "❌"], ["-", "❌", "-"], ["❌", "-", "-"]]
        result = ttt.check_winner()
        assert result == "❌"

    def test_no_winner_mixed_board(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
        result = ttt.check_winner()
        assert result is None

    def test_partial_row_not_winner(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "⭕", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.check_winner()
        assert result is None

    def test_partial_col_not_winner(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "-", "-"], ["⭕", "-", "-"], ["-", "-", "-"]]
        result = ttt.check_winner()
        assert result is None

    def test_custom_board_parameter(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        custom = [["⭕", "⭕", "⭕"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.check_winner(custom)
        assert result == "⭕"

    def test_default_board_parameter_none_uses_self(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["❌", "❌", "❌"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.check_winner(None)
        assert result == "❌"


class TestTicTacToeEvaluateBoard:
    def test_player1_winning_board(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.player1_move = "⭕"
        ttt.player2_move = "❌"
        board = [["⭕", "⭕", "⭕"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.evaluate_board(board)
        # player1 wins → returns -1 (note: type annotation says None but actually returns int)
        assert result == -1

    def test_player2_winning_board(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.player1_move = "⭕"
        ttt.player2_move = "❌"
        board = [["❌", "❌", "❌"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.evaluate_board(board)
        # player2 wins → returns 1
        assert result == 1

    def test_empty_board_returns_zero(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.player1_move = "⭕"
        ttt.player2_move = "❌"
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        result = ttt.evaluate_board(board)
        assert result == 0

    def test_draw_board_returns_zero(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.player1_move = "⭕"
        ttt.player2_move = "❌"
        board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
        result = ttt.evaluate_board(board)
        assert result == 0

    def test_partial_board_no_winner(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.player1_move = "⭕"
        ttt.player2_move = "❌"
        board = [["⭕", "-", "-"], ["-", "❌", "-"], ["-", "-", "-"]]
        result = ttt.evaluate_board(board)
        assert result == 0


class TestTicTacToeIsFull:
    def test_empty_board_not_full(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        assert ttt.is_full() is False

    def test_full_board(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
        assert ttt.is_full() is True

    def test_one_empty_cell(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "-"]]
        assert ttt.is_full() is False

    def test_custom_board_parameter(self):
        ttt = TicTacToe.__new__(TicTacToe)
        ttt.board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        custom = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
        assert ttt.is_full(custom) is True


class TestTicTacToeGetAvailableMoves:
    def test_empty_board_all_moves(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        moves = ttt.get_available_moves(board)
        assert len(moves) == 9

    def test_full_board_no_moves(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "❌"]]
        moves = ttt.get_available_moves(board)
        assert len(moves) == 0

    def test_one_move_available(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["⭕", "❌", "⭕"], ["❌", "⭕", "❌"], ["❌", "⭕", "-"]]
        moves = ttt.get_available_moves(board)
        assert moves == [8]

    def test_center_available(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["⭕", "❌", "⭕"], ["❌", "-", "❌"], ["❌", "⭕", "❌"]]
        moves = ttt.get_available_moves(board)
        assert moves == [4]

    def test_corners_available(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "❌", "-"], ["❌", "⭕", "❌"], ["-", "❌", "-"]]
        moves = ttt.get_available_moves(board)
        assert sorted(moves) == [0, 2, 6, 8]

    def test_move_indices_map_correctly(self):
        """Index i maps to row i//3 and column i%3."""
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        moves = ttt.get_available_moves(board)
        assert 0 in moves
        assert 4 in moves
        assert 8 in moves


class TestTicTacToeMinimaxMakeMove:
    def test_creates_new_board(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = ttt.minimax_make_move(board, 0, "⭕")
        assert new_board[0][0] == "⭕"
        assert board[0][0] == "-"  # Original unchanged

    def test_does_not_modify_original(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = ttt.minimax_make_move(board, 4, "❌")
        assert board[1][1] == "-"
        assert new_board[1][1] == "❌"

    def test_center_move(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = ttt.minimax_make_move(board, 4, "⭕")
        assert new_board[1][1] == "⭕"

    def test_corner_move(self):
        ttt = TicTacToe.__new__(TicTacToe)
        board = [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        new_board = ttt.minimax_make_move(board, 8, "❌")
        assert new_board[2][2] == "❌"


class TestTicTacToeInit:
    def test_default_board(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>", "bot": False})()
        ttt = TicTacToe(player)
        assert ttt.board == [["-", "-", "-"], ["-", "-", "-"], ["-", "-", "-"]]
        assert ttt.game_over is False
        assert ttt.winner is None
        assert ttt.player1_move == "⭕"
        assert ttt.player2_move == "❌"

    def test_default_player2_is_tanjun(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>", "bot": False})()
        ttt = TicTacToe(player)
        assert ttt.player2 == "tanjun"

    def test_bot_difficulty_range(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>", "bot": False})()
        ttt = TicTacToe(player)
        assert 1 <= ttt.bot_difficulty <= 5


# ==================== Connect4 ====================


class TestConnect4CheckWinner:
    def test_empty_board_no_winner(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        assert c4.check_winner() is None

    def test_horizontal_win(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[5][0] = "🔴"
        c4.board[5][1] = "🔴"
        c4.board[5][2] = "🔴"
        c4.board[5][3] = "🔴"
        assert c4.check_winner() == "🔴"

    def test_horizontal_win_yellow(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[4][1] = "🟡"
        c4.board[4][2] = "🟡"
        c4.board[4][3] = "🟡"
        c4.board[4][4] = "🟡"
        assert c4.check_winner() == "🟡"

    def test_vertical_win(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[2][3] = "🔴"
        c4.board[3][3] = "🔴"
        c4.board[4][3] = "🔴"
        c4.board[5][3] = "🔴"
        assert c4.check_winner() == "🔴"

    def test_diagonal_top_left_to_bottom_right(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[2][0] = "🔴"
        c4.board[3][1] = "🔴"
        c4.board[4][2] = "🔴"
        c4.board[5][3] = "🔴"
        assert c4.check_winner() == "🔴"

    def test_diagonal_top_right_to_bottom_left(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[2][6] = "🟡"
        c4.board[3][5] = "🟡"
        c4.board[4][4] = "🟡"
        c4.board[5][3] = "🟡"
        assert c4.check_winner() == "🟡"

    def test_no_winner_mixed(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[5][0] = "🔴"
        c4.board[5][1] = "🟡"
        c4.board[5][2] = "🔴"
        c4.board[5][3] = "🟡"
        assert c4.check_winner() is None

    def test_three_in_a_row_not_winner(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[5][0] = "🔴"
        c4.board[5][1] = "🔴"
        c4.board[5][2] = "🔴"
        # Only 3, need 4 for a win
        assert c4.check_winner() is None


class TestConnect4IsFull:
    def test_empty_board_not_full(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        assert c4.is_full() is False

    def test_full_board(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["🔴" if (r + c) % 2 == 0 else "🟡" for c in range(7)] for r in range(6)]
        assert c4.is_full() is True

    def test_one_empty_cell(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["🔴" for _ in range(7)] for _ in range(6)]
        c4.board[0][3] = "⚫"
        assert c4.is_full() is False


class TestConnect4GetAvailableMoves:
    def test_empty_board_has_moves(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        moves = c4.get_available_moves()
        # get_available_moves returns bottom-most empty cell per column
        assert len(moves) > 0

    def test_full_board_no_moves(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["🔴" for _ in range(7)] for _ in range(6)]
        moves = c4.get_available_moves()
        assert len(moves) == 0

    def test_moves_are_row_col_tuples(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        moves = c4.get_available_moves()
        for move in moves:
            assert len(move) == 2
            row, col = move
            assert 0 <= row < 6
            assert 0 <= col < 7


class TestConnect4AvailableColumns:
    def test_empty_board_all_columns(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        cols = c4.available_columns()
        assert cols == [0, 1, 2, 3, 4, 5, 6]

    def test_first_row_filled(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[0] = ["🔴"] * 7
        cols = c4.available_columns()
        assert cols == []

    def test_partial_fill(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        c4.board = [["⚫"] * 7 for _ in range(6)]
        c4.board[0][3] = "🔴"
        cols = c4.available_columns()
        assert 3 not in cols
        assert 0 in cols


class TestConnect4MinimaxMakeMove:
    def test_creates_new_board(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        board = [["⚫"] * 7 for _ in range(6)]
        new_board = c4.minimax_make_move(board, (5, 3), "🔴")
        assert new_board[5][3] == "🔴"
        assert board[5][3] == "⚫"

    def test_does_not_modify_original(self):
        c4 = Connect4.__new__(Connect4)
        c4.rows = 6
        c4.columns = 7
        c4.empty_cell = "⚫"
        board = [["⚫"] * 7 for _ in range(6)]
        new_board = c4.minimax_make_move(board, (5, 0), "🟡")
        assert board[5][0] == "⚫"
        assert new_board[5][0] == "🟡"


class TestConnect4Init:
    def test_default_board_size(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>"})()
        c4 = Connect4(player)
        assert len(c4.board) == 6
        assert len(c4.board[0]) == 7
        assert c4.game_over is False
        assert c4.winner is None

    def test_default_player2_is_tanjun(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>"})()
        c4 = Connect4(player)
        assert c4.player2 == "tanjun"

    def test_default_pieces(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>"})()
        c4 = Connect4(player)
        assert c4.player1_move == "🔴"
        assert c4.player2_move == "🟡"
        assert c4.empty_cell == "⚫"

    def test_empty_board(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>"})()
        c4 = Connect4(player)
        for row in c4.board:
            for cell in row:
                assert cell == "⚫"

    def test_bot_difficulty_range(self):
        player = type("FakePlayer", (), {"id": 1, "mention": "<@1>"})()
        c4 = Connect4(player)
        assert 1 <= c4.bot_difficulty <= 5