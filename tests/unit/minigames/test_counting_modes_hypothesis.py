"""Hypothesis property tests for counting modes math."""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from minigames.counting_modes import (
    get_correct_next_number,
    get_first_number,
    modeMap,
    number_to_romeal,
    romeal_to_number,
)
from models import CountingMode


@pytest.mark.unit
class TestRomanHypothesis:
    @given(n=st.integers(min_value=1, max_value=3999))
    @settings(max_examples=100)
    def test_roman_roundtrip(self, n: int):
        roman = number_to_romeal(n)
        assert isinstance(roman, str)
        assert romeal_to_number(roman) == n

    @given(n=st.integers(min_value=4000, max_value=5000))
    @settings(max_examples=20)
    def test_out_of_range_returns_error_string(self, n: int):
        result = number_to_romeal(n)
        assert "Invalid input" in result


@pytest.mark.unit
class TestCountingModesHypothesis:
    @given(
        mode=st.sampled_from(list(modeMap.keys())),
        progress=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=80)
    def test_get_first_number_defined_for_all_modes(self, mode: CountingMode, progress: int):
        first = get_first_number(mode)
        assert first is not None
        _ = get_correct_next_number(mode, first if mode != CountingMode.ROMEAN else progress)

    @given(n=st.integers(min_value=0, max_value=20))
    @settings(max_examples=40)
    def test_normal_mode_increments_by_one(self, n: int):
        assert get_correct_next_number(CountingMode.NORMAL, n) == n + 1

    @given(n=st.integers(min_value=1, max_value=30))
    @settings(max_examples=40)
    def test_double_mode_doubles(self, n: int):
        assert get_correct_next_number(CountingMode.DOUBLE, n) == n * 2

    @given(n=st.integers(min_value=1, max_value=10))
    @settings(max_examples=30)
    def test_triple_mode_triples(self, n: int):
        assert get_correct_next_number(CountingMode.TRIPLE, n) == n * 3

    @given(n=st.integers(min_value=0, max_value=900))
    @settings(max_examples=40)
    def test_hundreds_mode_adds_100(self, n: int):
        assert get_correct_next_number(CountingMode.HUNDREDS, n) == n + 100

    @given(n=st.integers(min_value=0, max_value=100))
    @settings(max_examples=40)
    def test_square_mode_next_is_perfect_square(self, n: int):
        nxt = get_correct_next_number(CountingMode.SQUARE, n)
        root = int(math.isqrt(nxt))
        assert root * root == nxt
