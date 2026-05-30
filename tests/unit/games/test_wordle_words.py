"""Unit tests for wordle word lists."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.wordle_words import words as wordle_words


@pytest.mark.unit
class TestWordleWords:
    @pytest.mark.parametrize("locale", ["en", "de", "fr"])
    def test_allowed_and_possible_words_load(self, locale: str):
        allowed = wordle_words.allowed_words(locale)
        possible = wordle_words.possible_words(locale)
        assert len(allowed) > 0
        assert len(possible) > 0

    @pytest.mark.parametrize("locale", ["en", "de"])
    def test_possible_words_subset_of_allowed(self, locale: str):
        allowed = set(wordle_words.allowed_words(locale))
        possible = wordle_words.possible_words(locale)
        assert all(word in allowed for word in possible)

    @pytest.mark.parametrize("locale", ["en", "de"])
    def test_words_are_five_letters_for_latin_locales(self, locale: str):
        for word in wordle_words.possible_words(locale)[:50]:
            assert len(word) == 5
            assert word.isalpha()


@pytest.mark.unit
class TestWordleWordsHypothesis:
    @given(
        locale=st.sampled_from(["en", "de", "fr", "es", "pt"]),
        index=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=30)
    def test_allowed_word_at_index_is_string(self, locale: str, index: int):
        allowed = wordle_words.allowed_words(locale)
        if index < len(allowed):
            assert isinstance(allowed[index], str)
            assert len(allowed[index]) > 0
