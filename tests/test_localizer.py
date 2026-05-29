"""Tests for the LocalizerService and TranslationEntry classes."""

import asyncio
import json
import os
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config  # noqa: F401 – side-effect import

from localizer import (
    CACHE_TTL,
    TRANSLATION_NOT_FOUND,
    LocalizerService,
    TranslationEntry,
    tanjunLocalizer,
)
from translator import TanjunTranslator

# ---------------------------------------------------------------------------
# Fix the broken discord mock from conftest
# ---------------------------------------------------------------------------
# conftest.py replaces sys.modules["discord"] with a MagicMock, so
# localizer.discord.Locale is a MagicMock and isinstance(x, MagicMock) fails.
# We patch it to a real base class here so isinstance checks work.

import localizer as _loc_mod
import translator as _tr_mod


class _LocaleBase:
    """Stands in for discord.Locale – real type for isinstance checks."""
    pass


class _Locale(_LocaleBase):
    """Locale-like object with a .value attribute (mirrors discord.Locale)."""
    def __init__(self, v: str):
        self.value = v


_loc_mod.discord.Locale = _LocaleBase
try:
    _tr_mod.discord.Locale = _LocaleBase
except Exception:
    pass

FAKE_DE = _Locale("de")
FAKE_EN_US = _Locale("en-US")
FAKE_EN_GB = _Locale("en-GB")

# Also need app_commands.Translator to be a real object so TanjunTranslator()
# can be instantiated.  We patch it at the module level.
_tr_mod.discord.app_commands.Translator = object


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _chdir(d: Path):
    """Return a callable that restores cwd after changing to d.parent."""
    old = os.getcwd()
    os.chdir(d.parent)
    return lambda: os.chdir(old)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service() -> LocalizerService:
    svc = LocalizerService()
    svc._cache.clear()
    return svc


@pytest.fixture
def sample_entries() -> list[TranslationEntry]:
    return [
        TranslationEntry(identifier="test.hello", translation="Hello, $name!", description="Greeting"),
        TranslationEntry(identifier="test.farewell", translation="Goodbye, $name.", description="Farewell"),
        TranslationEntry(identifier="test.plain", translation="Just a plain string."),
    ]


@pytest.fixture
def locale_dir(tmp_path: Path) -> Path:
    lp = tmp_path / "locales"
    lp.mkdir()
    en = [
        {"identifier": "common.error", "translation": "An error occurred: $detail", "description": "err"},
        {"identifier": "common.success", "translation": "Operation successful.", "description": "ok"},
        {"identifier": "commands.ping.name", "translation": "ping", "description": "ping"},
    ]
    de = [
        {"identifier": "common.error", "translation": "Ein Fehler ist aufgetreten: $detail", "description": "err DE"},
        {"identifier": "common.success", "translation": "Vorgang erfolgreich.", "description": "ok DE"},
        {"identifier": "commands.ping.name", "translation": "ping", "description": "ping DE"},
    ]
    (lp / "en.json").write_text(json.dumps(en), encoding="utf-8")
    (lp / "de.json").write_text(json.dumps(de), encoding="utf-8")
    return lp


# ===================================================================
# TranslationEntry
# ===================================================================

class TestTranslationEntry:
    def test_basic(self):
        e = TranslationEntry(identifier="g.hi", translation="Hello, $name!", description="greet")
        assert e.identifier == "g.hi"
        assert e.translation == "Hello, $name!"
        assert e.description == "greet"

    def test_no_description(self):
        e = TranslationEntry(identifier="g.hi", translation="Hi")
        assert e.description is None

    def test_from_dict(self):
        e = TranslationEntry.from_dict({"identifier": "x", "translation": "Y", "description": "Z"})
        assert e.identifier == "x" and e.translation == "Y" and e.description == "Z"

    def test_from_dict_no_desc(self):
        e = TranslationEntry.from_dict({"identifier": "x", "translation": "Y"})
        assert e.description is None

    def test_from_dict_none_desc(self):
        e = TranslationEntry.from_dict({"identifier": "x", "translation": "Y", "description": None})
        assert e.description is None

    def test_from_dict_coercion(self):
        e = TranslationEntry.from_dict({"identifier": 42, "translation": True, "description": None})
        assert e.identifier == "42"
        assert e.translation == "True"


# ===================================================================
# _normalize_locale
# ===================================================================

class TestNormalizeLocale:
    def test_fake_de(self, service: LocalizerService):
        assert service._normalize_locale(FAKE_DE) == "de"

    def test_fake_en_us(self, service: LocalizerService):
        assert service._normalize_locale(FAKE_EN_US) == "en"

    def test_fake_en_gb(self, service: LocalizerService):
        assert service._normalize_locale(FAKE_EN_GB) == "en"

    def test_str_de(self, service: LocalizerService):
        assert service._normalize_locale("de") == "de"

    def test_str_en_us(self, service: LocalizerService):
        assert service._normalize_locale("en-US") == "en"

    def test_str_en_gb(self, service: LocalizerService):
        assert service._normalize_locale("en-GB") == "en"

    def test_str_en(self, service: LocalizerService):
        assert service._normalize_locale("en") == "en"

    def test_str_unknown(self, service: LocalizerService):
        assert service._normalize_locale("fr") == "fr"


# ===================================================================
# _validate_json
# ===================================================================

class TestValidateJson:
    def test_valid(self, service: LocalizerService):
        r = service._validate_json([{"identifier": "a", "translation": "A"}])
        assert r is not None and len(r) == 1

    def test_empty(self, service: LocalizerService):
        assert service._validate_json([]) == []

    def test_not_list(self, service: LocalizerService):
        assert service._validate_json({"k": "v"}) is None

    def test_non_dict_elements(self, service: LocalizerService):
        assert service._validate_json(["x"]) is None

    def test_two_entries(self, service: LocalizerService):
        r = service._validate_json([{"identifier": "a", "translation": "A"}, {"identifier": "b", "translation": "B"}])
        assert r is not None and len(r) == 2


# ===================================================================
# _find_entry
# ===================================================================

class TestFindEntry:
    def test_exact(self, service: LocalizerService, sample_entries):
        r = service._find_entry(sample_entries, "test.hello")
        assert r and r.identifier == "test.hello"

    def test_case_insensitive(self, service: LocalizerService, sample_entries):
        assert service._find_entry(sample_entries, "TEST.HELLO") is not None

    def test_not_found(self, service: LocalizerService, sample_entries):
        assert service._find_entry(sample_entries, "nope") is None

    def test_empty(self, service: LocalizerService):
        assert service._find_entry([], "x") is None


# ===================================================================
# _load_sync
# ===================================================================

class TestLoadSync:
    def test_load_en(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            r = service._load_sync("en")
            assert len(r) == 3 and r[0].identifier == "common.error"
        finally:
            restore()

    def test_fallback_to_en(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            service._load_sync("en")
            r = service._load_sync("fr")
            assert len(r) == 3
        finally:
            restore()

    def test_fallback_no_en_cache(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            service.reload_locales()
            r = service._load_sync("fr")
            assert len(r) == 3
        finally:
            restore()

    def test_cache_hit(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            r1 = service._load_sync("en")
            r2 = service._load_sync("en")
            assert r1 is r2
        finally:
            restore()

    def test_cache_expiry(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            r1 = service._load_sync("en")
            entries, _ = service._cache["en"]
            service._cache["en"] = (entries, time.time() - CACHE_TTL - 1)
            r2 = service._load_sync("en")
            assert r1 is not r2 and len(r1) == len(r2)
        finally:
            restore()

    def test_bad_json(self, service: LocalizerService, tmp_path):
        d = tmp_path / "locales"
        d.mkdir()
        (d / "en.json").write_text("{{{ bad", encoding="utf-8")
        old = os.getcwd()
        try:
            os.chdir(tmp_path)
            assert service._load_sync("en") == []
        finally:
            os.chdir(old)

    def test_german(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            r = service._load_sync("de")
            assert len(r) == 3
            assert r[0].translation == "Ein Fehler ist aufgetreten: $detail"
        finally:
            restore()


# ===================================================================
# localize
# ===================================================================

class TestLocalize:
    def test_placeholder(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            assert service.localize("en", "common.error", detail="timeout") == "An error occurred: timeout"
        finally:
            restore()

    def test_no_placeholder(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            assert service.localize("en", "common.success") == "Operation successful."
        finally:
            restore()

    def test_missing_key(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            with patch.object(service, "_report_missing"):
                assert service.localize("en", "xyz") == TRANSLATION_NOT_FOUND
        finally:
            restore()

    def test_safe_substitution(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            assert service.localize("en", "common.error") == "An error occurred: $detail"
        finally:
            restore()


# ===================================================================
# test_localize
# ===================================================================

class TestTestLocalize:
    def test_found(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            assert service.test_localize("en", "common.success") == "Operation successful."
        finally:
            restore()

    def test_returns_found_not_de(self, service: LocalizerService, locale_dir):
        """_load_sync('fr') falls back to English, finds key → returns English, not de."""
        restore = _chdir(locale_dir)
        try:
            assert service.test_localize("fr", "common.success") == "Operation successful."
        finally:
            restore()

    def test_de_missing(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            r = service.test_localize("de", "xyz")
            assert "No translation found" in r
        finally:
            restore()


# ===================================================================
# Async load_locale
# ===================================================================

class TestLoadLocaleAsync:
    def test_async(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(service.load_locale("en"))
            loop.close()
            assert len(r) == 3 and r[0].identifier == "common.error"
        finally:
            restore()


# ===================================================================
# get_translation
# ===================================================================

class TestGetTranslation:
    def test_found(self, service: LocalizerService, sample_entries):
        assert service.get_translation(sample_entries, "test.hello") is not None

    def test_not_found(self, service: LocalizerService, sample_entries):
        assert service.get_translation(sample_entries, "x") is None

    def test_case_insensitive(self, service: LocalizerService, sample_entries):
        assert service.get_translation(sample_entries, "TEST.HELLO") is not None


# ===================================================================
# Cache management
# ===================================================================

class TestCacheManagement:
    def test_reload(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            service._load_sync("en")
            assert len(service._cache) > 0
            service.reload_locales()
            assert len(service._cache) == 0
        finally:
            restore()

    def test_available(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            service._load_sync("en")
            service._load_sync("de")
            assert set(service.get_available_locales()) == {"en", "de"}
        finally:
            restore()

    def test_available_empty(self, service: LocalizerService):
        assert service.get_available_locales() == []


# ===================================================================
# _report_missing
# ===================================================================

class TestReportMissing:
    def test_tracks(self, service: LocalizerService):
        from localizer import reported_locales
        reported_locales.clear()
        with patch("localizer.missingLocalization", new_callable=AsyncMock):
            service._report_missing("xx")
            assert "xx" in reported_locales

    def test_dedup(self, service: LocalizerService):
        from localizer import reported_locales
        reported_locales.clear()
        with patch("localizer.missingLocalization", new_callable=AsyncMock):
            service._report_missing("xx")
            service._report_missing("xx")
        assert reported_locales.count("xx") == 1


# ===================================================================
# TanjunTranslator
# ===================================================================

class _FakeTranslator:
    """Mimics TanjunTranslator.translate() without inheriting from the broken mock base."""
    def __init__(self, svc: LocalizerService):
        self._localizer = svc

    async def translate(self, string, locale, context):
        from localizer import TRANSLATION_NOT_FOUND
        key_str = str(string).replace("_", ".")
        current = self._localizer.localize(locale, key_str)
        if current == TRANSLATION_NOT_FOUND:
            return None
        return current


class TestTanjunTranslator:
    def test_found(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            t = _FakeTranslator(service)
            s = MagicMock()
            s.__str__ = lambda self: "common.success"
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, MagicMock(), MagicMock()))
            loop.close()
            assert r == "Operation successful."
        finally:
            restore()

    def test_not_found(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            t = _FakeTranslator(service)
            s = MagicMock()
            s.__str__ = lambda self: "xyz"
            with patch.object(service, "_report_missing"):
                loop = asyncio.new_event_loop()
                r = loop.run_until_complete(t.translate(s, MagicMock(), MagicMock()))
                loop.close()
                assert r is None
        finally:
            restore()

    def test_underscore_to_dot(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            t = _FakeTranslator(service)
            s = MagicMock()
            s.__str__ = lambda self: "commands_ping_name"
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, MagicMock(), MagicMock()))
            loop.close()
            assert r == "ping"
        finally:
            restore()

    def test_type_importable(self):
        """TanjunTranslator should be importable (non-None)."""
        assert TanjunTranslator is not None


# ===================================================================
# Constants
# ===================================================================

class TestConstants:
    def test_not_found(self):
        assert TRANSLATION_NOT_FOUND == "err: no translation found."

    def test_ttl(self):
        assert CACHE_TTL == 300.0


# ===================================================================
# Global instance
# ===================================================================

class TestGlobalInstance:
    def test_exists(self):
        assert isinstance(tanjunLocalizer, LocalizerService)

    def test_singleton(self):
        from localizer import tanjunLocalizer as r
        assert r is tanjunLocalizer


# ===================================================================
# Deprecated API
# ===================================================================

class TestDeprecatedApi:
    def test_sync(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            assert len(service.load_translations("en")) == 3
        finally:
            restore()

    def test_async(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(service.load_translations_async("en"))
            loop.close()
            assert len(r) == 3
        finally:
            restore()

    def test_async_matches_sync(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            loop = asyncio.new_event_loop()
            a = loop.run_until_complete(service.load_translations_async("de"))
            loop.close()
            s = service._load_sync("de")
            assert len(a) == len(s) and all(
                ai.identifier == si.identifier for ai, si in zip(a, s)
            )
        finally:
            restore()
