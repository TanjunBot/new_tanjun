"""Unit tests for flag quiz similarity and hint logic."""

from __future__ import annotations

import difflib
import random
from unittest.mock import patch

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st


def get_similarity(guess: str, answer: str) -> float:
    return difflib.SequenceMatcher(None, guess.lower(), answer.lower()).ratio() * 100


def get_hint(word: str) -> str:
    chars = list(word.lower())
    blanks = ["_"] * len(chars)
    num_reveals = max(1, len(chars) // 3)
    reveal_positions = random.sample(range(len(chars)), num_reveals)
    for pos in reveal_positions:
        blanks[pos] = chars[pos]
    return "".join(blanks)


@pytest.mark.unit
class TestFlagQuizLogic:
    def test_identical_strings_full_similarity(self):
        assert get_similarity("Germany", "Germany") == 100.0

    def test_different_strings_lower_similarity(self):
        assert get_similarity("France", "Germany") < 50.0

    def test_case_insensitive(self):
        assert get_similarity("germany", "GERMANY") == 100.0

    def test_hint_reveals_some_characters(self):
        with patch("random.sample", side_effect=lambda population, k: population[:k]):
            hint = get_hint("Germany")
            assert "_" in hint
            assert "g" in hint.lower()


@pytest.mark.unit
class TestFlagQuizHypothesis:
    @given(text=st.text(min_size=1, max_size=20))
    @settings(max_examples=50)
    def test_similarity_bounded(self, text: str):
        sim = get_similarity(text, text)
        assert 0.0 <= sim <= 100.0
        assert sim == 100.0

    @given(
        guess=st.text(min_size=1, max_size=15),
        answer=st.text(min_size=1, max_size=15),
    )
    @settings(max_examples=30, deadline=None)
    def test_similarity_symmetric_order(self, guess: str, answer: str):
        assume(len(guess) <= 32 and len(answer) <= 32)
        s1 = get_similarity(guess, answer)
        s2 = get_similarity(answer, guess)
        assert abs(s1 - s2) < 1.0

    @given(word=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=3, max_size=12))
    @settings(max_examples=30)
    def test_hint_same_length_as_word(self, word: str):
        with patch("random.sample", side_effect=lambda population, count: population[:count]):
            hint = get_hint(word)
            assert len(hint) == len(word)
