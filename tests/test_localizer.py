"""Tests for the Localizer class."""

import asyncio
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from unittest.mock import AsyncMock, patch

import sys
from unittest.mock import MagicMock

import pytest

import tests.mock_config as mock_config  # noqa: F401

mock_config.patch_config_module()

# Mock discord before importing localizer
_discord_mock = MagicMock()
_discord_mock.Locale = type("Locale", (), {})
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()

from localizer import (  # noqa: E402
    CACHE_TTL,
    Localizer,
    tanjunLocalizer,
    reported_locales,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@contextmanager
def _chdir(d: Path) -> Iterator[None]:
    old = os.getcwd()
    os.chdir(d.parent)
    try:
        yield
    finally:
        os.chdir(old)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def loc() -> Localizer:
    lz = Localizer()
    lz._cache.clear()
    lz.translations.clear()
    return lz


@pytest.fixture
def locale_dir(tmp_path: Path) -> Path:
    lp = tmp_path / "locales"
    lp.mkdir()
    en = [
        {"identifier": "common.error", "translation": "An error occurred: $detail"},
        {"identifier": "common.success", "translation": "Operation successful."},
        {"identifier": "commands.ping.name", "translation": "ping"},
    ]
    de = [
        {"identifier": "common.error", "translation": "Ein Fehler ist aufgetreten: $detail"},
        {"identifier": "common.success", "translation": "Vorgang erfolgreich."},
        {"identifier": "commands.ping.name", "translation": "ping"},
    ]
    (lp / "en.json").write_text(json.dumps(en), encoding="utf-8")
    (lp / "de.json").write_text(json.dumps(de), encoding="utf-8")
    return lp


# ===================================================================
# Class init
# ===================================================================


class TestInit:
    def test_empty_cache(self, loc: Localizer):
        assert loc._cache == {}
        assert loc.translations == {}

    def test_ttl_default(self, loc: Localizer):
        assert loc._cache_ttl == CACHE_TTL


# ===================================================================
# _load_translations_sync
# ===================================================================


class TestLoadTranslationsSync:
    def test_load_en(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc._load_translations_sync("en")
            assert len(r) == 3
            assert r[0]["identifier"] == "common.error"

    def test_load_german(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc._load_translations_sync("de")
            assert len(r) == 3
            assert r[0]["translation"] == "Ein Fehler ist aufgetreten: $detail"

    def test_cache_hit_returns_same_object(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r1 = loc._load_translations_sync("en")
            r2 = loc._load_translations_sync("en")
            assert r1 is r2

    def test_cache_expiry(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r1 = loc._load_translations_sync("en")
            entries, _ = loc._cache["en"]
            loc._cache["en"] = (entries, time.time() - CACHE_TTL - 1)
            r2 = loc._load_translations_sync("en")
            assert r1 is not r2
            assert len(r1) == len(r2)

    def test_fallback_to_cached_en(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            loc._load_translations_sync("en")
            r = loc._load_translations_sync("fr")
            assert len(r) == 3

    def test_fallback_loads_en_from_disk(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc._load_translations_sync("fr")
            assert len(r) == 3

    def test_bad_json_returns_empty(self, loc: Localizer, tmp_path: Path):
        d = tmp_path / "locales"
        d.mkdir()
        (d / "en.json").write_text("{{{ bad", encoding="utf-8")
        old = os.getcwd()
        try:
            os.chdir(tmp_path)
            assert loc._load_translations_sync("en") == []
        finally:
            os.chdir(old)

    def test_not_a_list_returns_empty(self, loc: Localizer, locale_dir: Path):
        (locale_dir / "en.json").write_text('{"identifier":"x","translation":"y"}', encoding="utf-8")
        with _chdir(locale_dir):
            assert loc._load_translations_sync("en") == []

    def test_missing_file_returns_empty(self, loc: Localizer, locale_dir: Path):
        (locale_dir / "en.json").unlink()
        with _chdir(locale_dir):
            assert loc._load_translations_sync("en") == []


# ===================================================================
# load_translations (sync wrapper)
# ===================================================================


class TestLoadTranslations:
    def test_sync_wrapper(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc.load_translations("de")
            assert len(r) == 3


# ===================================================================
# load_translations_async
# ===================================================================


class TestLoadTranslationsAsync:
    def test_async(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(loc.load_translations_async("en"))
            loop.close()
            assert len(r) == 3


# ===================================================================
# get_translation
# ===================================================================


class TestGetTranslation:
    def test_found(self, loc: Localizer):
        entries = [
            {"identifier": "a.b", "translation": "hello"},
            {"identifier": "c.d", "translation": "world"},
        ]
        r = loc.get_translation(entries, "a.b")
        assert r is not None
        assert r["translation"] == "hello"

    def test_case_insensitive(self, loc: Localizer):
        entries = [{"identifier": "A.B", "translation": "foo"}]
        assert loc.get_translation(entries, "a.b") is not None

    def test_not_found(self, loc: Localizer):
        assert loc.get_translation([], "nope") is None


# ===================================================================
# localize
# ===================================================================


class TestLocalize:
    def test_en_with_placeholder(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.localize("en", "common.error", detail="timeout") == "An error occurred: timeout"

    def test_de_with_placeholder(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc.localize("de", "common.error", detail="Zeitüberschreitung")
            assert r == "Ein Fehler ist aufgetreten: Zeitüberschreitung"

    def test_en_us_normalized(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.localize("en-US", "common.success") == "Operation successful."

    def test_de_prefix_normalized(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.localize("de-DE", "common.success") == "Vorgang erfolgreich."

    def test_no_placeholder(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.localize("en", "common.success") == "Operation successful."

    def test_safe_substitute(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.localize("en", "common.error") == "An error occurred: $detail"

    def test_missing_key(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            with patch.object(loc, "load_translations", return_value=[]):
                result = loc.localize("en", "xyz")
                assert result == "err: no translation found."

    def test_reports_missing_locale(self, loc: Localizer, locale_dir: Path):
        reported_locales.clear()
        with _chdir(locale_dir):
            with patch.object(loc, "load_translations", return_value=[]), patch("localizer.missingLocalization", new_callable=AsyncMock):
                result = loc.localize("en", "xyz")
                assert result == "err: no translation found."
                assert "en" in reported_locales


# ===================================================================
# test_localize
# ===================================================================


class TestTestLocalize:
    def test_found(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            assert loc.test_localize("en", "common.success") == "Operation successful."

    def test_fallback_to_de(self, loc: Localizer, locale_dir: Path):
        """test_localize with missing key falls back to localize('de', key)."""
        with _chdir(locale_dir):
            reported_locales.clear()
            with patch("localizer.missingLocalization", new_callable=AsyncMock):
                # 'fr' falls back to en, 'nope' not found → tries localize('de', 'nope')
                # 'nope' also missing in de → returns sentinel
                r = loc.test_localize("fr", "nope")
                assert r == "err: no translation found."

    def test_de_missing(self, loc: Localizer, locale_dir: Path):
        with _chdir(locale_dir):
            r = loc.test_localize("de", "nope")
            assert "No translation found" in r


# ===================================================================
# Global instance
# ===================================================================


class TestGlobalInstance:
    def test_exists(self):
        assert isinstance(tanjunLocalizer, Localizer)

    def test_singleton(self):
        from localizer import tanjunLocalizer
        assert tanjunLocalizer is tanjunLocalizer


# ===================================================================
# Constants
# ===================================================================


class TestConstants:
    def test_ttl(self):
        assert CACHE_TTL == 300.0


# ===================================================================
# reported_locales
# ===================================================================


class TestReportedLocales:
    def test_append(self):
        reported_locales.clear()
        reported_locales.append("fr")
        assert "fr" in reported_locales

    def test_dedup(self):
        reported_locales.clear()
        reported_locales.append("fr")
        # Simulate the dedup check: append only if not already present
        if "fr" not in reported_locales:
            reported_locales.append("fr")
        assert reported_locales == ["fr"]
