"""Unit tests for hangman game helpers."""

from __future__ import annotations

import string

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.hangman import get_guessed_letters, hangmanSteps, wrong_letters


class TestGetGuessedLetters:
    def test_full_word_guess_returns_word(self):
        assert get_guessed_letters(["hello"], "hello") == "hello"

    def test_reveals_matching_letters(self):
        assert get_guessed_letters(["e", "l"], "hello") == "_ell_"

    def test_spaces_preserved(self):
        assert get_guessed_letters(["a"], "a b") == "a _"

    def test_no_guesses_all_underscores(self):
        assert get_guessed_letters([], "cat") == "___"


class TestWrongLetters:
    def test_counts_wrong_single_letters(self):
        assert wrong_letters(["x", "y"], "hello") == 2

    def test_ignores_correct_letters(self):
        assert wrong_letters(["h", "e"], "hello") == 0

    def test_ignores_full_word_guess_in_count(self):
        assert wrong_letters(["hello", "x"], "hello") == 1

    def test_empty_guesses(self):
        assert wrong_letters([], "hello") == 0


class TestHangmanSteps:
    def test_step_count(self):
        assert len(hangmanSteps) == 12

    def test_first_step_empty(self):
        assert hangmanSteps[0].strip() == ""


@pytest.mark.unit
class TestHangmanHypothesis:
    @given(
        word=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=12),
        guesses=st.lists(
            st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=1),
            max_size=8,
        ),
    )
    @settings(max_examples=80)
    def test_guessed_letters_length_matches_word(self, word: str, guesses: list[str]):
        result = get_guessed_letters(guesses, word)
        assert len(result) == len(word)

    @given(
        word=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=10),
        guesses=st.lists(
            st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=1),
            max_size=6,
        ),
    )
    @settings(max_examples=80)
    def test_wrong_letters_non_negative(self, word: str, guesses: list[str]):
        assert wrong_letters(guesses, word) >= 0

    @given(word=st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=8))
    @settings(max_examples=40)
    def test_all_correct_letters_zero_wrong(self, word: str):
        guesses = list(set(word))
        assert wrong_letters(guesses, word) == 0
