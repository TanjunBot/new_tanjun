"""Unit tests for country flag assets."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from commands.games.country_flags import flags


@pytest.mark.unit
class TestCountryFlags:
    def test_flags_list_not_empty(self):
        assert len(flags.flags) > 0

    def test_all_flags_are_png(self):
        assert all(f.endswith(".png") for f in flags.flags)

    def test_random_flag_in_list(self):
        with patch("commands.games.country_flags.flags.random.choice", side_effect=lambda xs: xs[0]):
            chosen = flags.random_flag()
            assert chosen in flags.flags

    def test_get_flag_img_path(self):
        name = flags.flags[0]
        path = flags.get_flag_img(name)
        assert path == f"commands/games/country_flags/{name}"
        assert os.path.exists(path)


@pytest.mark.unit
class TestCountryFlagsHypothesis:
    @given(index=st.integers(min_value=0, max_value=5))
    @settings(max_examples=10)
    def test_flag_files_exist_on_disk(self, index: int):
        if index >= len(flags.flags):
            return
        flag_file = flags.flags[index]
        assert os.path.isfile(f"commands/games/country_flags/{flag_file}")
