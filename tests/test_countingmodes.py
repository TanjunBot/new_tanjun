"""Tests for counting modes math (primes, fibonacci, roman numerals, mode logic).

These functions in minigames/countingmodes.py are pure math — no Discord dependency.
"""

import math
import sys
from unittest.mock import MagicMock, patch

# Mock discord module before importing countingmodes
discord_mock = MagicMock()
discord_mock.User = type("User", (), {})
discord_mock.Message = type("Message", (), {})
sys.modules["discord"] = discord_mock

# Mock api module
api_mock = MagicMock()
sys.modules["api"] = api_mock

# Mock localizer
localizer_mock = MagicMock()
sys.modules["localizer"] = localizer_mock
sys.modules["localizer"].tanjunLocalizer = MagicMock()

# Mock utility
utility_mock = MagicMock()
sys.modules["utility"] = utility_mock

from minigames.counting_modes import (
    get_correct_next_number,
    get_first_number,
    get_goal,
    modeMap,
    number_to_romeal,
    romeal_to_number,
)


class TestRomanNumerals:
    def test_number_to_romeal_basic(self):
        assert number_to_romeal(1) == "I"
        assert number_to_romeal(4) == "IV"
        assert number_to_romeal(5) == "V"
        assert number_to_romeal(9) == "IX"
        assert number_to_romeal(10) == "X"
        assert number_to_romeal(50) == "L"
        assert number_to_romeal(100) == "C"
        assert number_to_romeal(500) == "D"
        assert number_to_romeal(1000) == "M"

    def test_number_to_romeal_complex(self):
        assert number_to_romeal(42) == "XLII"
        assert number_to_romeal(199) == "CXCIX"
        assert number_to_romeal(2024) == "MMXXIV"
        assert number_to_romeal(3999) == "MMMCMXCIX"

    def test_number_to_romeal_zero(self):
        assert number_to_romeal(0) == "0"

    def test_number_to_romeal_out_of_range(self):
        result = number_to_romeal(4000)
        assert "Invalid input" in str(result)
        result = number_to_romeal(-1)
        assert "Invalid input" in str(result)

    def test_romeal_to_number_basic(self):
        assert romeal_to_number("I") == 1
        assert romeal_to_number("V") == 5
        assert romeal_to_number("X") == 10
        assert romeal_to_number("L") == 50
        assert romeal_to_number("C") == 100
        assert romeal_to_number("D") == 500
        assert romeal_to_number("M") == 1000

    def test_romeal_to_number_complex(self):
        assert romeal_to_number("IV") == 4
        assert romeal_to_number("IX") == 9
        assert romeal_to_number("XLII") == 42
        assert romeal_to_number("CXCIX") == 199
        assert romeal_to_number("MMXXIV") == 2024

    def test_romeal_to_number_case_insensitive(self):
        assert romeal_to_number("iv") == 4
        assert romeal_to_number("XlIi") == 42

    def test_romeal_to_number_invalid_quadruple(self):
        result = romeal_to_number("IIII")
        assert math.isnan(result)

    def test_roundtrip(self):
        for n in [1, 4, 9, 42, 99, 100, 399, 1999, 3999]:
            assert romeal_to_number(number_to_romeal(n)) == n


class TestGetCorrectNextNumber:
    def test_mode_1_normal(self):
        assert get_correct_next_number(1, 0) == 1
        assert get_correct_next_number(1, 5) == 6
        assert get_correct_next_number(1, 100) == 101

    def test_mode_2_negative(self):
        assert get_correct_next_number(2, 0) == -1
        assert get_correct_next_number(2, -5) == -6

    def test_mode_3_reverse(self):
        assert get_correct_next_number(3, 101) == 100
        assert get_correct_next_number(3, 5) == 4

    def test_mode_4_prime(self):
        assert get_correct_next_number(4, 2) == 3
        assert get_correct_next_number(4, 3) == 5
        assert get_correct_next_number(4, 13) == 17
        assert get_correct_next_number(4, 97) == 101

    def test_mode_5_even(self):
        assert get_correct_next_number(5, 0) == 2
        assert get_correct_next_number(5, 2) == 4
        assert get_correct_next_number(5, 100) == 102

    def test_mode_6_odd(self):
        assert get_correct_next_number(6, -1) == 1
        assert get_correct_next_number(6, 1) == 3
        assert get_correct_next_number(6, 99) == 101

    def test_mode_7_fibonacci(self):
        assert get_correct_next_number(7, -1) == 0
        assert get_correct_next_number(7, 0) == 1
        assert get_correct_next_number(7, 1) == 2
        assert get_correct_next_number(7, 2) == 3
        assert get_correct_next_number(7, 3) == 5
        assert get_correct_next_number(7, 13) == 21

    def test_mode_8_double(self):
        assert get_correct_next_number(8, 1) == 2
        assert get_correct_next_number(8, 2) == 4
        assert get_correct_next_number(8, 32) == 64

    def test_mode_9_triple(self):
        assert get_correct_next_number(9, 1) == 3
        assert get_correct_next_number(9, 3) == 9
        assert get_correct_next_number(9, 27) == 81

    def test_mode_10_hundreds(self):
        assert get_correct_next_number(10, 0) == 100
        assert get_correct_next_number(10, 100) == 200

    def test_mode_11_binary(self):
        # Binary mode stores the integer value; display layer converts to binary
        assert get_correct_next_number(11, 0) == 1
        assert get_correct_next_number(11, 1) == 2
        assert get_correct_next_number(11, 10) == 11
        assert get_correct_next_number(11, 99) == 100

    def test_mode_12_roman(self):
        # Mode 12 expects integer progress (roman conversion is in counting())
        assert get_correct_next_number(12, 0) == "I"
        assert get_correct_next_number(12, 1) == "II"
        result = get_correct_next_number(12, 10)
        assert number_to_romeal(romeal_to_number(result)) == result  # Valid roman
        assert romeal_to_number(result) == 11

    def test_mode_13_square(self):
        assert get_correct_next_number(13, 0) == 1
        assert get_correct_next_number(13, 1) == 4
        assert get_correct_next_number(13, 4) == 9
        assert get_correct_next_number(13, 100) == 121

    def test_mode_14_cube(self):
        assert get_correct_next_number(14, 0) == 1
        assert get_correct_next_number(14, 1) == 8
        assert get_correct_next_number(14, 8) == 27
        assert get_correct_next_number(14, 125) == 216


class TestGetFirstNumber:
    def test_first_numbers(self):
        assert get_first_number(1) == 0
        assert get_first_number(2) == 0
        assert get_first_number(3) == 101
        assert get_first_number(4) == 0
        assert get_first_number(5) == 0
        assert get_first_number(6) == -1
        assert get_first_number(7) == -1
        assert get_first_number(8) == 1
        assert get_first_number(9) == 1
        assert get_first_number(10) == 0
        assert get_first_number(11) == 0
        assert get_first_number(12) == 0
        assert get_first_number(13) == 0
        assert get_first_number(14) == 0


class TestModeMap:
    def test_all_modes_defined(self):
        assert len(modeMap) == 14
        assert modeMap[1] == "normal"
        assert modeMap[14] == "cube"

    def test_all_modes_have_first_number(self):
        for mode_id in modeMap:
            first = get_first_number(mode_id)
            assert first is not None

    def test_all_modes_have_goal_function(self):
        for mode_id in modeMap:
            with patch("minigames.counting_modes.random.randint") as mock_randint:
                mock_randint.return_value = 50
                if mode_id == 4:
                    # primes list has ~47 elements; index 7 = 17 is safe
                    mock_randint.return_value = 7
                goal = get_goal(mode_id)
                assert goal is not None
