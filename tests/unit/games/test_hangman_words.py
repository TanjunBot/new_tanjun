"""Unit tests for hangman word lists."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.hangman_words import words


@pytest.mark.unit
class TestHangmanWords:
    @pytest.mark.parametrize("locale", ["en", "de", "fr"])
    def test_words_load(self, locale: str):
        word_list = words.words(locale)
        assert len(word_list) > 10

    def test_words_are_non_empty_strings(self):
        for word in words.words("en")[:30]:
            assert isinstance(word, str)
            assert len(word) > 0


@pytest.mark.unit
class TestHangmanWordsHypothesis:
    @given(locale=st.sampled_from(["en", "de", "fr", "es"]))
    @settings(max_examples=10)
    def test_word_list_not_empty(self, locale: str):
        word_list = words.words(locale)
        assert len(word_list) >= 1
