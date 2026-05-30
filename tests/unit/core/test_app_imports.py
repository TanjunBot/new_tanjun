"""Smoke tests ensuring core modules import without runtime errors."""

from __future__ import annotations


def test_utils_embeds_imports():
    import utils.embeds  # noqa: F401


def test_utility_imports():
    import utility  # noqa: F401
