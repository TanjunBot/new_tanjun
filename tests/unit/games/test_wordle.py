"""Unit tests for wordle language normalization."""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


def normalize_wordle_language(language: str, locale: str) -> str:
    if language == "own":
        language = locale
    if language in ["en-US", "en-GB"]:
        return "en"
    if language in ["zh-CH", "zh-TW"]:
        return "zh"
    if language in ["es-419", "es-ES"]:
        return "es"
    if language in ["pt-BR", "pt-PT"]:
        return "pt"
    return language


@pytest.mark.unit
class TestWordleLanguageNormalization:
    @pytest.mark.parametrize(
        ("language", "locale", "expected"),
        [
            ("own", "en-US", "en"),
            ("en-GB", "de", "en"),
            ("de", "en-US", "de"),
            ("es-ES", "fr", "es"),
            ("pt-BR", "en", "pt"),
        ],
    )
    def test_normalize(self, language: str, locale: str, expected: str):
        assert normalize_wordle_language(language, locale) == expected


@pytest.mark.unit
class TestWordleHypothesis:
    @given(locale=st.sampled_from(["en-US", "de", "fr", "ja"]))
    @settings(max_examples=15)
    def test_own_uses_locale(self, locale: str):
        result = normalize_wordle_language("own", locale)
        assert result in (locale, "en", "zh", "es", "pt") or result == locale.split("-")[0]
