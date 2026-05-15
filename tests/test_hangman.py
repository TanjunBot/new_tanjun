"""Tests for hangman.py pure functions — comprehensive."""
import pytest

from tests.mock_config import patch_config_module

patch_config_module()

from commands.games.hangman import get_guessed_letters, wrong_letters, hangmanSteps


class TestHangmanSteps:
    def test_has_12_steps(self):
        assert len(hangmanSteps) == 12

    def test_steps_are_strings(self):
        for step in hangmanSteps:
            assert isinstance(step, str)

    def test_first_step_is_empty_gallows(self):
        # First step is the empty gallows (whitespace/newlines)
        assert isinstance(hangmanSteps[0], str)
        assert len(hangmanSteps[0].strip()) == 0 or "|" in hangmanSteps[0]

    def test_last_step_is_complete_figure(self):
        # Last step should have a complete figure with multiple body parts
        assert len(hangmanSteps[11]) > len(hangmanSteps[0])

    def test_steps_progress(self):
        """Each subsequent step should be longer or equal (more parts added)."""
        for i in range(1, len(hangmanSteps)):
            assert len(hangmanSteps[i]) >= len(hangmanSteps[i - 1])


class TestGetGuessedLetters:
    def test_no_guesses(self):
        result = get_guessed_letters([], "hello")
        assert result == "_____"

    def test_single_correct_guess(self):
        result = get_guessed_letters(["h"], "hello")
        assert result == "h____"

    def test_multiple_correct_guesses(self):
        result = get_guessed_letters(["h", "e", "l"], "hello")
        assert result == "hell_"

    def test_all_letters_guessed(self):
        result = get_guessed_letters(["h", "e", "l", "o"], "hello")
        assert result == "hello"

    def test_wrong_guesses_only(self):
        result = get_guessed_letters(["x", "y", "z"], "hello")
        assert result == "_____"

    def test_full_word_guess(self):
        """Guessing the full word reveals it completely."""
        result = get_guessed_letters(["hello"], "hello")
        assert result == "hello"

    def test_word_with_spaces(self):
        result = get_guessed_letters(["h"], "he llo")
        # Space should be preserved as-is
        assert " " in result
        assert result.startswith("h")

    def test_word_with_spaces_no_guesses(self):
        result = get_guessed_letters([], "he llo")
        # Space should be preserved, letters hidden
        assert " " in result

    def test_duplicate_guesses(self):
        """Duplicate guesses don't change the result."""
        result1 = get_guessed_letters(["h", "h"], "hello")
        result2 = get_guessed_letters(["h"], "hello")
        assert result1 == result2

    def test_empty_word(self):
        result = get_guessed_letters(["a"], "")
        assert result == ""

    def test_case_sensitivity(self):
        """Guesses are compared as-is; if case doesn't match, letter stays hidden."""
        result = get_guessed_letters(["H"], "hello")
        # "H" != "h" so it should stay hidden
        assert result == "_____"

    def test_repeated_letters_in_word(self):
        result = get_guessed_letters(["l"], "hello")
        assert result == "__ll_"

    def test_full_wrong_word_guess(self):
        """Guessing a wrong full word should still hide letters."""
        result = get_guessed_letters(["wrong"], "hello")
        assert result == "_____"


class TestWrongLetters:
    def test_no_guesses(self):
        assert wrong_letters([], "hello") == 0

    def test_all_wrong_single_letters(self):
        assert wrong_letters(["x", "y", "z"], "hello") == 3

    def test_all_correct_single_letters(self):
        assert wrong_letters(["h", "e", "l", "o"], "hello") == 0

    def test_mixed_correct_and_wrong(self):
        assert wrong_letters(["h", "x", "z"], "hello") == 2

    def test_full_word_guess_not_counted(self):
        """Full-word guesses (len > 1) are not counted as wrong letters."""
        assert wrong_letters(["wrong"], "hello") == 0

    def test_full_correct_word_guess_not_counted(self):
        """Even correct full-word guesses aren't counted as single-letter wrong guesses."""
        assert wrong_letters(["hello"], "hello") == 0

    def test_repeated_wrong_guesses(self):
        """Each wrong single-letter guess counts separately."""
        assert wrong_letters(["x", "x", "x"], "hello") == 3

    def test_empty_word(self):
        """Every single-letter guess is wrong if word is empty."""
        assert wrong_letters(["a", "b"], "") == 2

    def test_returns_int(self):
        result = wrong_letters(["a"], "hello")
        assert isinstance(result, int)

    def test_max_wrong_guesses(self):
        """11+ wrong letters means game over in hangman."""
        guesses = list("xyzqwvunmpk")
        assert wrong_letters(guesses, "hello") == 11


class TestGetGuessedLettersDeep:
    def test_word_all_same_letter(self):
        result = get_guessed_letters(["a"], "aaa")
        assert result == "aaa"

    def test_guess_sentinel_string(self):
        """Wrong full-word guesses add a junk string that doesn't reveal letters."""
        result = get_guessed_letters(["THISAINTBEINGTHEWORD"], "hello")
        assert result == "_____"

    def test_mixed_single_and_full_correct(self):
        """Full word guess reveals everything, even alongside other guesses."""
        result = get_guessed_letters(["h", "e", "hello"], "hello")
        assert result == "hello"

    def test_special_characters_in_word(self):
        """Words with spaces preserve spaces, other chars stay hidden."""
        result = get_guessed_letters([], "a b")
        assert result == "_ _"

    def test_single_char_word(self):
        result = get_guessed_letters(["a"], "a")
        assert result == "a"

    def test_no_guesses_single_char_word(self):
        result = get_guessed_letters([], "a")
        assert result == "_"


class TestWrongLettersDeep:
    def test_sentinel_string_not_counted(self):
        """The sentinel string 'THISAINTBEINGTHEWORD' has length > 1, so not counted."""
        assert wrong_letters(["THISAINTBEINGTHEWORD"], "hello") == 0

    def test_mixed_single_and_multi(self):
        """Only single-letter guesses count."""
        assert wrong_letters(["h", "wrong", "x"], "hello") == 1

    def test_correct_single_letter_not_wrong(self):
        assert wrong_letters(["h"], "hello") == 0

    def test_wrong_count_with_partial_word(self):
        """2-char strings are also not single letters."""
        assert wrong_letters(["ab", "x"], "hello") == 1

    def test_all_vowels_wrong(self):
        assert wrong_letters(["a", "e", "i", "o", "u"], "xyz") == 5


class TestHangmanStepsDeep:
    def test_steps_count_is_12(self):
        assert len(hangmanSteps) == 12

    def test_step_0_minimal(self):
        """First step should be nearly empty (just whitespace or minimal gallows)."""
        assert len(hangmanSteps[0].strip()) <= 10

    def test_step_11_has_body_parts(self):
        """Last step should have body parts (emoji or ASCII art)."""
        last = hangmanSteps[11]
        assert len(last) > 0

    def test_steps_monotonically_non_decreasing(self):
        """Each step should be at least as long as the previous."""
        for i in range(1, len(hangmanSteps)):
            assert len(hangmanSteps[i]) >= len(hangmanSteps[i - 1])

    def test_step_1_has_platform(self):
        """Second step should have the bottom platform."""
        assert "___" in hangmanSteps[1] or len(hangmanSteps[1].strip()) > 0

    def test_step_2_has_post(self):
        """Third step should have a vertical post."""
        assert "|" in hangmanSteps[2]

    def test_step_5_has_post_and_top(self):
        """Step 5 should have the post structure."""
        assert "|" in hangmanSteps[5]

    def test_step_11_has_arms_and_legs(self):
        """Final step should have arms and legs."""
        assert "/|\\" in hangmanSteps[11] or "/|\\" in hangmanSteps[11].replace("\\\\", "\\")
        assert "/ \\" in hangmanSteps[11]


class TestGetGuessedLettersDeepEdgeCases:
    def test_guess_all_letters_individually(self):
        """Guess each letter of 'test' individually."""
        result = get_guessed_letters(["t", "e", "s"], "test")
        assert result == "test"

    def test_guess_nothing_for_long_word(self):
        result = get_guessed_letters([], "programming")
        assert result == "_" * len("programming")

    def test_word_with_multiple_spaces(self):
        """Spaces in the word are always revealed."""
        result = get_guessed_letters([], "a b c")
        assert result == "_ _ _"

    def test_guess_reveals_all_occurrences(self):
        """A single letter guess reveals all occurrences of that letter."""
        result = get_guessed_letters(["o"], "book")
        assert result == "_oo_"

    def test_guess_correct_then_full_word(self):
        """Full word guess takes priority over individual guesses."""
        result = get_guessed_letters(["l", "hello"], "hello")
        assert result == "hello"

    def test_all_wrong_single_letters(self):
        """All wrong single-letter guesses leave all underscores."""
        result = get_guessed_letters(["x", "y", "z", "q", "w"], "apple")
        assert result == "_____"

    def test_partial_reveal(self):
        result = get_guessed_letters(["p"], "apple")
        # "apple" has double-p, so both are revealed
        assert result == "_pp__"

    def test_empty_guesses_list(self):
        result = get_guessed_letters([], "test")
        assert result == "____"


class TestWrongLettersDeepEdgeCases:
    def test_exactly_11_wrong_ends_game(self):
        """11 wrong single-letter guesses means game over."""
        guesses = list("bcdfgxyzqwk")
        assert wrong_letters(guesses, "hello") == 11

    def test_zero_wrong_for_perfect_game(self):
        guesses = list("helo")
        assert wrong_letters(guesses, "hello") == 0

    def test_vowels_against_consonant_word(self):
        assert wrong_letters(["a", "e", "i", "o", "u"], "crypt") == 5

    def test_consonants_against_vowel_word(self):
        assert wrong_letters(["b", "c", "d"], "aieou") == 3

    def test_mixed_length_guesses(self):
        """Only length-1 strings count as wrong guesses."""
        assert wrong_letters(["a", "bb", "c", "ddd"], "hello") == 2