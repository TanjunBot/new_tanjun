"""Tests for the LocalizerService and TranslationEntry classes."""

import asyncio
import json
import os
import time
from collections.abc import Callable
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Fix the broken discord mock from conftest
# ---------------------------------------------------------------------------
# conftest.py replaces sys.modules["discord"] with a MagicMock, so
# localizer.discord.Locale is a MagicMock and isinstance(x, MagicMock) fails.
# We patch it to a real base class here so isinstance checks work.

# Create real base classes for discord.Locale and app_commands.Translator
# BEFORE importing the tanjun modules so the real TanjunTranslator class
# inherits from a proper Translator base (not a MagicMock).


class _LocaleBase:
    """Stands in for discord.Locale – real type for isinstance checks."""

    pass


class _Locale(_LocaleBase):
    """Locale-like object with a .value attribute (mirrors discord.Locale)."""

    def __init__(self, v: str):
        self.value = v


class _TranslatorBase:
    """Stands in for discord.app_commands.Translator – real base class for isinstance checks."""

    async def load(self) -> None:
        pass

    async def translate(self, string: object, locale: object, context: object) -> str | None:  # noqa: ANN001
        return None

    async def unload(self) -> None:
        pass


# Patch the discord mock BEFORE importing localizer/translator modules
_orig_discord = __import__("sys").modules.get("discord")
if _orig_discord is not None:
    _orig_discord.Locale = _LocaleBase
    _orig_discord.app_commands = (
        MagicMock() if isinstance(_orig_discord.app_commands, MagicMock) else _orig_discord.app_commands
    )
    _orig_discord.app_commands.Translator = _TranslatorBase

import tests.mock_config  # noqa: F401, E402 – side-effect import
from localizer import (  # noqa: E402
    CACHE_TTL,
    TRANSLATION_NOT_FOUND,
    LocalizerService,
    TranslationEntry,
    tanjunLocalizer,
)
from translator import TanjunTranslator  # noqa: E402

FAKE_DE = _Locale("de")
FAKE_EN_US = _Locale("en-US")
FAKE_EN_GB = _Locale("en-GB")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _chdir(d: Path) -> Callable[[], None]:
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
        assert service._normalize_locale("sv") == "en"


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
    def test_exact(self, service: LocalizerService, sample_entries: list[TranslationEntry]) -> None:
        r = service._find_entry(sample_entries, "test.hello")
        assert r and r.identifier == "test.hello"

    def test_case_insensitive(self, service: LocalizerService, sample_entries: list[TranslationEntry]) -> None:
        assert service._find_entry(sample_entries, "TEST.HELLO") is not None

    def test_not_found(self, service: LocalizerService, sample_entries: list[TranslationEntry]) -> None:
        assert service._find_entry(sample_entries, "nope") is None

    def test_underscore_dot_fallback(self, service: LocalizerService) -> None:
        entries = [TranslationEntry(identifier="setup_name", translation="setup")]
        assert service._find_entry(entries, "setup.name") is not None
        assert service._find_entry(entries, "setup.name").translation == "setup"

    def test_empty(self, service: LocalizerService) -> None:
        assert service._find_entry([], "x") is None


# ===================================================================
# _load_sync
# ===================================================================


class TestLoadSync:
    def test_load_en(self, service: LocalizerService, locale_dir: Path) -> None:
        restore = _chdir(locale_dir)
        try:
            r = service._load_sync("en")
            assert len(r) == 3 and r[0].identifier == "common.error"
        finally:
            restore()

    def test_fallback_to_en(self, service: LocalizerService, locale_dir: Path) -> None:
        restore = _chdir(locale_dir)
        try:
            service._load_sync("en")
            r = service._load_sync("fr")
            assert len(r) == 3
        finally:
            restore()

    def test_fallback_no_en_cache(self, service: LocalizerService, locale_dir: Path) -> None:
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

    def test_bad_json(self, service: LocalizerService, tmp_path: Path) -> None:
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
        """_load_sync('fr') falls back to English, finds key -> returns English, not de."""
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
        from localizer import reported_missing

        reported_missing.clear()
        with patch("localizer.missingLocalization", new_callable=AsyncMock):
            service._report_missing("xx", "test.key")
            assert ("xx", "test.key") in reported_missing

    def test_dedup(self, service: LocalizerService):
        from localizer import reported_missing

        reported_missing.clear()
        with patch("localizer.missingLocalization", new_callable=AsyncMock):
            service._report_missing("xx", "test.key")
            service._report_missing("xx", "test.key")
        assert len(reported_missing) == 1

    def test_dedup_per_key(self, service: LocalizerService):
        from localizer import reported_missing

        reported_missing.clear()
        with patch("localizer.missingLocalization", new_callable=AsyncMock):
            service._report_missing("xx", "test.key.one")
            service._report_missing("xx", "test.key.two")
        assert len(reported_missing) == 2


# ===================================================================
# TanjunTranslator
# ===================================================================


class TestTanjunTranslator:
    """Tests for the real TanjunTranslator class (not a fake)."""

    def test_importable(self):
        """TanjunTranslator should be importable (non-None)."""
        assert TanjunTranslator is not None

    def test_default_localizer(self):
        """TanjunTranslator() uses the global tanjunLocalizer by default."""
        t = TanjunTranslator()
        assert t._localizer is tanjunLocalizer

    def test_custom_localizer(self, service: LocalizerService):
        """TanjunTranslator(localizer=svc) uses the provided localizer."""
        t = TanjunTranslator(localizer=service)
        assert t._localizer is service

    def test_is_translator_subclass(self):
        """TanjunTranslator is a proper subclass of app_commands.Translator."""
        assert issubclass(TanjunTranslator, _TranslatorBase)

    def test_found(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            t = TanjunTranslator(localizer=service)
            s = MagicMock()
            s.__str__ = lambda self: "common.success"
            context = MagicMock()
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, MagicMock(), context))
            loop.close()
            assert r == "Operation successful."
        finally:
            restore()

    def test_not_found(self, service: LocalizerService, locale_dir):
        restore = _chdir(locale_dir)
        try:
            t = TanjunTranslator(localizer=service)
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
            t = TanjunTranslator(localizer=service)
            s = MagicMock()
            s.__str__ = lambda self: "commands_ping_name"
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, MagicMock(), MagicMock()))
            loop.close()
            assert r == "ping"
        finally:
            restore()

    def test_translate_with_locale_enum(self, service: LocalizerService, locale_dir: Path):
        """translate() works with a discord.Locale-like enum object (not just strings)."""
        restore = _chdir(locale_dir)
        try:
            t = TanjunTranslator(localizer=service)
            s = MagicMock()
            s.__str__ = lambda self: "common.success"
            locale_obj = FAKE_DE  # _Locale("de")
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, locale_obj, MagicMock()))
            loop.close()
            # FAKE_DE has value "de", so it finds the German translation
            assert r == "Vorgang erfolgreich."
        finally:
            restore()

    def test_translate_fallback_locale(self, service: LocalizerService, locale_dir: Path):
        """translate() falls back to English for unsupported locale values."""
        restore = _chdir(locale_dir)
        try:
            t = TanjunTranslator(localizer=service)
            s = MagicMock()
            s.__str__ = lambda self: "common.success"
            unsupported_locale = _Locale("fr")
            loop = asyncio.new_event_loop()
            r = loop.run_until_complete(t.translate(s, unsupported_locale, MagicMock()))
            loop.close()
            # '_normalize_locale("fr")' now returns "en" because unknown locales
            # are silently mapped to English to avoid creating spam "missing
            # localization" GitHub issues.  The English file is loaded directly.
            assert r == "Operation successful."
        finally:
            restore()

    def test_translate_returns_none_for_missing(self, service: LocalizerService, locale_dir: Path):
        """translate() returns None for missing keys (not TRANSLATION_NOT_FOUND)."""
        restore = _chdir(locale_dir)
        try:
            t = TanjunTranslator(localizer=service)
            s = MagicMock()
            s.__str__ = lambda self: "nonexistent.key"
            with patch.object(service, "_report_missing"):
                loop = asyncio.new_event_loop()
                r = loop.run_until_complete(t.translate(s, MagicMock(), MagicMock()))
                loop.close()
                assert r is None
        finally:
            restore()


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
        # tanjunLocalizer is a singleton - verify two imports return the same instance
        import localizer as _localizer_mod

        assert tanjunLocalizer is _localizer_mod.tanjunLocalizer


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

    def test_async_matches_sync(self, service: LocalizerService, locale_dir: Path) -> None:
        restore = _chdir(locale_dir)
        try:
            loop = asyncio.new_event_loop()
            a = loop.run_until_complete(service.load_translations_async("de"))
            loop.close()
            s = service._load_sync("de")
            assert len(a) == len(s) and all(ai.identifier == si.identifier for ai, si in zip(a, s, strict=True))
        finally:
            restore()
