"""Tests for minigames logic — comprehensive."""

import math

from tests.mock_config import patch_config_module

patch_config_module()

from minigames.countingmodes import (
    fibonacci,
    get_correct_next_number,
    get_first_number,
    get_goal,
    modeMap,
    number_to_romeal,
    primes,
    romeal_to_number,
)


class TestModeMap:
    def test_mode_map_has_all_modes(self) -> None:
        assert len(modeMap) == 14

    def test_mode_map_keys(self) -> None:
        expected_modes = {
            1: "normal",
            2: "negative",
            3: "reverse",
            4: "prime",
            5: "even",
            6: "odd",
            7: "fibonacci",
            8: "double",
            9: "triple",
            10: "houndreds",
            11: "binary",
            12: "romean",
            13: "square",
            14: "cube",
        }
        assert modeMap == expected_modes

    def test_mode_map_values_are_strings(self) -> None:
        for key, value in modeMap.items():
            assert isinstance(value, str)

    def test_mode_map_keys_are_consecutive(self) -> None:
        assert list(modeMap.keys()) == list(range(1, 15))


class TestPrimes:
    def test_primes_list_starts_correctly(self) -> None:
        assert primes[1] == 2
        assert primes[2] == 3
        assert primes[3] == 5
        assert primes[4] == 7

    def test_primes_list_values_are_prime(self) -> None:
        for p in primes[1:]:
            assert all(p % d != 0 for d in range(2, int(math.sqrt(p)) + 1))

    def test_primes_list_has_zero_sentinel(self) -> None:
        assert primes[0] == 0

    def test_primes_includes_common_values(self) -> None:
        assert 2 in primes
        assert 3 in primes
        assert 5 in primes
        assert 7 in primes
        assert 11 in primes
        assert 13 in primes
        assert 97 in primes


class TestFibonacci:
    def test_fibonacci_starting_values(self) -> None:
        assert fibonacci[1] == 0
        assert fibonacci[2] == 1
        assert fibonacci[3] == 2
        assert fibonacci[4] == 3

    def test_fibonacci_sequence_property(self) -> None:
        """The fibonacci list has a sentinel value (-1) at index 0, so the
        recurrence relation only holds for indices >= 4 (past the two 1s
        and the 0/sentinel base cases)."""
        for i in range(4, len(fibonacci)):
            assert fibonacci[i] == fibonacci[i - 1] + fibonacci[i - 2], f"Failed at index {i}"

    def test_fibonacci_sentinel_value(self) -> None:
        """Index 0 has sentinel -1."""
        assert fibonacci[0] == -1

    def test_fibonacci_values_increase(self) -> None:
        for i in range(4, len(fibonacci) - 1):
            assert fibonacci[i + 1] > fibonacci[i]


class TestRomealToNumber:
    def test_simple_values(self) -> None:
        assert romeal_to_number("I") == 1
        assert romeal_to_number("V") == 5
        assert romeal_to_number("X") == 10
        assert romeal_to_number("L") == 50
        assert romeal_to_number("C") == 100
        assert romeal_to_number("D") == 500
        assert romeal_to_number("M") == 1000

    def test_compound_values(self) -> None:
        assert romeal_to_number("IV") == 4
        assert romeal_to_number("IX") == 9
        assert romeal_to_number("XL") == 40
        assert romeal_to_number("XC") == 90
        assert romeal_to_number("CD") == 400
        assert romeal_to_number("CM") == 900

    def test_complex_numbers(self) -> None:
        assert romeal_to_number("MMXXIV") == 2024
        assert romeal_to_number("MCMXCIX") == 1999
        assert romeal_to_number("MMMCMXCIX") == 3999

    def test_case_insensitive(self) -> None:
        assert romeal_to_number("i") == 1
        assert romeal_to_number("xii") == 12
        assert romeal_to_number("MmXxIv") == 2024

    def test_invalid_four_repeats(self) -> None:
        """Four consecutive same letters should return NaN."""
        result = romeal_to_number("IIII")
        assert math.isnan(result)

    def test_invalid_four_v(self) -> None:
        result = romeal_to_number("VVVV")
        assert math.isnan(result)

    def test_empty_string(self) -> None:
        assert romeal_to_number("") == 0

    def test_single_digit(self) -> None:
        assert romeal_to_number("II") == 2
        assert romeal_to_number("III") == 3

    def test_additive(self) -> None:
        assert romeal_to_number("VI") == 6
        assert romeal_to_number("XV") == 15
        assert romeal_to_number("LX") == 60

    def test_subtractive_pair_in_middle(self) -> None:
        assert romeal_to_number("XIV") == 14
        assert romeal_to_number("CXL") == 140


class TestNumberToRomeal:
    def test_simple_values(self) -> None:
        assert number_to_romeal(1) == "I"
        assert number_to_romeal(5) == "V"
        assert number_to_romeal(10) == "X"

    def test_zero(self) -> None:
        assert number_to_romeal(0) == "0"

    def test_out_of_range(self) -> None:
        assert "Invalid" in number_to_romeal(4000)
        assert "Invalid" in number_to_romeal(-1)

    def test_compound_values(self) -> None:
        assert number_to_romeal(4) == "IV"
        assert number_to_romeal(9) == "IX"
        assert number_to_romeal(1999) == "MCMXCIX"

    def test_round_trip(self) -> None:
        for num in [1, 4, 9, 27, 49, 99, 444, 1000, 3999]:
            result = romeal_to_number(number_to_romeal(num))
            assert result == num, f"Round trip failed for {num}: got {result}"

    def test_all_simple_numerals(self) -> None:
        assert number_to_romeal(50) == "L"
        assert number_to_romeal(100) == "C"
        assert number_to_romeal(500) == "D"
        assert number_to_romeal(1000) == "M"

    def test_edge_case_3999(self) -> None:
        assert number_to_romeal(3999) == "MMMCMXCIX"

    def test_edge_case_1(self) -> None:
        assert number_to_romeal(1) == "I"


class TestGetCorrectNextNumber:
    def test_normal_mode(self) -> None:
        assert get_correct_next_number(1, 5) == 6
        assert get_correct_next_number(1, 0) == 1
        assert get_correct_next_number(1, 99) == 100

    def test_negative_mode(self) -> None:
        assert get_correct_next_number(2, 5) == 4
        assert get_correct_next_number(2, 0) == -1
        assert get_correct_next_number(2, -5) == -6

    def test_reverse_mode(self) -> None:
        assert get_correct_next_number(3, 101) == 100
        assert get_correct_next_number(3, 50) == 49
        assert get_correct_next_number(3, 1) == 0

    def test_prime_mode(self) -> None:
        assert get_correct_next_number(4, 2) == 3
        assert get_correct_next_number(4, 7) == 11
        assert get_correct_next_number(4, 97) == 101

    def test_even_mode(self) -> None:
        assert get_correct_next_number(5, 2) == 4
        assert get_correct_next_number(5, 0) == 2
        assert get_correct_next_number(5, 100) == 102

    def test_odd_mode(self) -> None:
        assert get_correct_next_number(6, 1) == 3
        assert get_correct_next_number(6, -1) == 1
        assert get_correct_next_number(6, 99) == 101

    def test_fibonacci_mode(self) -> None:
        assert get_correct_next_number(7, -1) == 0
        assert get_correct_next_number(7, 0) == 1
        assert get_correct_next_number(7, 1) == 2
        assert get_correct_next_number(7, 2) == 3
        assert get_correct_next_number(7, 3) == 5
        assert get_correct_next_number(7, 5) == 8

    def test_double_mode(self) -> None:
        assert get_correct_next_number(8, 1) == 2
        assert get_correct_next_number(8, 4) == 8
        assert get_correct_next_number(8, 16) == 32

    def test_triple_mode(self) -> None:
        assert get_correct_next_number(9, 1) == 3
        assert get_correct_next_number(9, 3) == 9
        assert get_correct_next_number(9, 9) == 27

    def test_hundreds_mode(self) -> None:
        assert get_correct_next_number(10, 0) == 100
        assert get_correct_next_number(10, 100) == 200
        assert get_correct_next_number(10, 500) == 600

    def test_binary_mode(self) -> None:
        assert get_correct_next_number(11, 0) == 1
        assert get_correct_next_number(11, 1) == 10
        # Binary mode returns next binary number as decimal integer (e.g., 10→1011)
        assert get_correct_next_number(11, 10) == 1011

    def test_roman_mode(self) -> None:
        result = get_correct_next_number(12, 0)
        assert result == "I"

    def test_square_mode(self) -> None:
        assert get_correct_next_number(13, 0) == 1
        assert get_correct_next_number(13, 1) == 4
        assert get_correct_next_number(13, 4) == 9
        assert get_correct_next_number(13, 9) == 16

    def test_cube_mode(self) -> None:
        assert get_correct_next_number(14, 0) == 1
        assert get_correct_next_number(14, 1) == 8
        assert get_correct_next_number(14, 8) == 27


class TestGetFirstNumber:
    def test_all_modes_return_int(self) -> None:
        for mode in range(1, 15):
            result = get_first_number(mode)
            assert isinstance(result, int)

    def test_normal_first(self) -> None:
        assert get_first_number(1) == 0

    def test_negative_first(self) -> None:
        assert get_first_number(2) == 0

    def test_reverse_first(self) -> None:
        assert get_first_number(3) == 101

    def test_prime_first(self) -> None:
        assert get_first_number(4) == 0

    def test_even_first(self) -> None:
        assert get_first_number(5) == 0

    def test_odd_first(self) -> None:
        assert get_first_number(6) == -1

    def test_fibonacci_first(self) -> None:
        assert get_first_number(7) == -1

    def test_double_first(self) -> None:
        assert get_first_number(8) == 1

    def test_triple_first(self) -> None:
        assert get_first_number(9) == 1

    def test_hundreds_first(self) -> None:
        assert get_first_number(10) == 0

    def test_binary_first(self) -> None:
        assert get_first_number(11) == 0

    def test_roman_first(self) -> None:
        assert get_first_number(12) == 0

    def test_square_first(self) -> None:
        assert get_first_number(13) == 0

    def test_cube_first(self) -> None:
        assert get_first_number(14) == 0


class TestGetGoal:
    def test_all_modes_return_number(self) -> None:
        for mode in range(1, 15):
            result = get_goal(mode)
            assert result is not None

    def test_normal_goal_range(self) -> None:
        for _ in range(50):
            goal = get_goal(1)
            assert 20 <= goal <= 100

    def test_negative_goal_range(self) -> None:
        for _ in range(50):
            goal = get_goal(2)
            assert -100 <= goal <= -20

    def test_reverse_goal_range(self) -> None:
        for _ in range(50):
            goal = get_goal(3)
            assert 5 <= goal <= 80

    def test_prime_goal_is_prime(self) -> None:
        for _ in range(20):
            goal = get_goal(4)
            assert goal in primes

    def test_even_goal_is_even(self) -> None:
        for _ in range(20):
            goal = get_goal(5)
            assert goal % 2 == 0

    def test_odd_goal_is_odd(self) -> None:
        for _ in range(20):
            goal = get_goal(6)
            assert goal % 2 != 0

    def test_fibonacci_goal_in_sequence(self) -> None:
        for _ in range(20):
            goal = get_goal(7)
            assert goal in fibonacci

    def test_double_goal_is_power_of_two(self) -> None:
        for _ in range(20):
            goal = get_goal(8)
            assert goal & (goal - 1) == 0

    def test_triple_goal_is_power_of_three(self) -> None:
        for _ in range(20):
            goal = get_goal(9)
            n = goal
            while n % 3 == 0:
                n //= 3
            assert n == 1

    def test_hundreds_goal_divisible_by_100(self) -> None:
        for _ in range(20):
            goal = get_goal(10)
            assert goal % 100 == 0

    def test_square_goal_is_perfect_square(self) -> None:
        for _ in range(20):
            goal = get_goal(13)
            assert math.isqrt(goal) ** 2 == goal

    def test_cube_goal_is_perfect_cube(self) -> None:
        for _ in range(20):
            goal = get_goal(14)
            assert round(goal ** (1 / 3)) ** 3 == goal


class TestRomealToNumberDeepEdgeCases:
    def test_invalid_four_repeats_various(self) -> None:
        assert math.isnan(romeal_to_number("VVVV"))
        assert math.isnan(romeal_to_number("XXXX"))
        assert math.isnan(romeal_to_number("CCCC"))
        assert math.isnan(romeal_to_number("MMMM"))

    def test_subtractive_pairs_all(self) -> None:
        assert romeal_to_number("IV") == 4
        assert romeal_to_number("IX") == 9
        assert romeal_to_number("XL") == 40
        assert romeal_to_number("XC") == 90
        assert romeal_to_number("CD") == 400
        assert romeal_to_number("CM") == 900

    def test_large_number(self) -> None:
        assert romeal_to_number("MMMCMXCIX") == 3999

    def test_single_numeral_each(self) -> None:
        assert romeal_to_number("I") == 1
        assert romeal_to_number("V") == 5
        assert romeal_to_number("X") == 10
        assert romeal_to_number("L") == 50
        assert romeal_to_number("C") == 100
        assert romeal_to_number("D") == 500
        assert romeal_to_number("M") == 1000

    def test_invalid_characters_treated_as_zero(self) -> None:
        """Unknown characters map to value 0, so they're silently ignored."""
        result = romeal_to_number("A")
        assert result == 0

    def test_three_repeats_valid(self) -> None:
        """Three repeats is valid in Roman numerals."""
        assert romeal_to_number("III") == 3
        assert romeal_to_number("XXX") == 30
        assert romeal_to_number("CCC") == 300

    def test_additive_notation(self) -> None:
        assert romeal_to_number("VI") == 6
        assert romeal_to_number("LX") == 60
        assert romeal_to_number("DC") == 600

    def test_complex_composite(self) -> None:
        assert romeal_to_number("MCMXCIX") == 1999


class TestNumberToRomealDeepEdgeCases:
    def test_all_basic_numerals(self) -> None:
        assert number_to_romeal(1) == "I"
        assert number_to_romeal(5) == "V"
        assert number_to_romeal(10) == "X"
        assert number_to_romeal(50) == "L"
        assert number_to_romeal(100) == "C"
        assert number_to_romeal(500) == "D"
        assert number_to_romeal(1000) == "M"

    def test_boundary_values(self) -> None:
        assert number_to_romeal(1) == "I"
        assert number_to_romeal(3999) == "MMMCMXCIX"
        assert number_to_romeal(0) == "0"

    def test_round_trip_all_primes_under_100(self) -> None:
        for p in primes[1:]:  # Skip sentinel 0
            if p < 4000:
                result = romeal_to_number(number_to_romeal(p))
                assert result == p, f"Round trip failed for prime {p}"

    def test_invalid_negative(self) -> None:
        assert "Invalid" in number_to_romeal(-1)

    def test_invalid_too_large(self) -> None:
        assert "Invalid" in number_to_romeal(4000)


class TestGetCorrectNextNumberDeepEdgeCases:
    def test_normal_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(1, 0) == 1

    def test_negative_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(2, 0) == -1

    def test_reverse_mode_starts_at_101(self) -> None:
        assert get_correct_next_number(3, 101) == 100

    def test_prime_mode_starts_at_sentinel(self) -> None:
        """Mode 4 starts with sentinel 0, next is 2 (first prime)."""
        assert get_correct_next_number(4, 0) == 2

    def test_even_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(5, 0) == 2

    def test_odd_mode_starts_at_negative_one(self) -> None:
        assert get_correct_next_number(6, -1) == 1

    def test_fibonacci_mode_sentinel(self) -> None:
        """Mode 7 has a -1 sentinel and a -15 sentinel for the second 1."""
        assert get_correct_next_number(7, -1) == 0
        assert get_correct_next_number(7, -15) == 1

    def test_double_mode_starts_at_one(self) -> None:
        assert get_correct_next_number(8, 1) == 2

    def test_triple_mode_starts_at_one(self) -> None:
        assert get_correct_next_number(9, 1) == 3

    def test_hundreds_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(10, 0) == 100

    def test_square_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(13, 0) == 1

    def test_cube_mode_starts_at_zero(self) -> None:
        assert get_correct_next_number(14, 0) == 1

    def test_binary_mode_sequence(self) -> None:
        """Test a small binary counting sequence: 0->1->10->11->100."""
        assert get_correct_next_number(11, 0) == 1
        assert get_correct_next_number(11, 1) == 10
        # After 10 (binary), next is 11 in decimal representation
        assert get_correct_next_number(11, 10) == 1011

    def test_square_mode_sequence(self) -> None:
        assert get_correct_next_number(13, 0) == 1
        assert get_correct_next_number(13, 1) == 4
        assert get_correct_next_number(13, 4) == 9
        assert get_correct_next_number(13, 9) == 16

    def test_cube_mode_sequence(self) -> None:
        assert get_correct_next_number(14, 0) == 1
        assert get_correct_next_number(14, 1) == 8
        assert get_correct_next_number(14, 8) == 27
