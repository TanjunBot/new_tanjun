from __future__ import annotations

import asyncio
import json
import time
from string import Template
from typing import Any, cast

import discord
from pydantic import BaseModel

from utility import missingLocalization
from utils.async_io import run_blocking

TRANSLATION_NOT_FOUND: str = "err: no translation found."

CACHE_TTL: float = 300.0  # 5 minutes

reported_missing: set[tuple[str, str]] = set()


class TranslationEntry(BaseModel):
    """A single translation entry with metadata.

    Attributes
    ----------
    identifier:
        The unique key for this translation (e.g. ``"greeting.hello"``).
    translation:
        The localized text, which may contain ``$variable`` placeholders
        for :class:`string.Template` substitution.
    description:
        An optional human-readable description of what this translation is for.
    """

    identifier: str
    translation: str
    description: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TranslationEntry:
        """Create a TranslationEntry from a raw JSON dict (backward compat)."""
        return cls(
            identifier=str(data.get("identifier", "")),
            translation=str(data.get("translation", "")),
            description=str(data.get("description")) if data.get("description") else None,
        )


class LocalizerService:
    """Typed service for loading, caching and rendering translations.

    Replaces the previous ``Localizer`` class with improved typing,
    Pydantic ``TranslationEntry`` models, and support for
    ``discord.Locale`` as a locale parameter.
    """

    def __init__(self) -> None:
        self._cache: dict[str, tuple[list[TranslationEntry], float]] = {}
        self._cache_ttl: float = CACHE_TTL

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_locale(locale: discord.Locale | str) -> str:
        """Normalize a locale value to a short identifier (e.g. ``de``, ``en``).

        Unsupported Discord locales (e.g. ``ja``, ``zh-TW``, ``es-419``) are
        silently mapped to ``"en"`` to avoid creating spam "missing localization"
        GitHub issues for languages that the bot does not ship locale files for.
        """
        raw = str(locale.value if isinstance(locale, discord.Locale) else locale)
        if raw in ("en", "en-US", "en-GB"):
        if raw.startswith("da"):
        if raw.startswith("hr"):
        if raw.startswith("bg"):
        if raw.startswith("it"):
        if raw.startswith("cs"):
        if raw.startswith("lt"):
        if raw in ("zh-CN", "zh-TW", "zh-Hans", "zh-Hant"):
        if raw.startswith("ja") or raw == "jp":
        if raw.startswith("id"):
        if raw in ("es", "es-ES", "es-419"):
        if raw.startswith("hu"):
        if raw.startswith("el"):
        if raw.startswith("nl"):
        if raw in ("zh-CN", "zh-Hans"):
        if raw in ("zh-TW", "zh-Hant"):
        if raw.startswith("fr"):
        if raw.startswith("fi"):
            return "en"
        if raw.startswith("de"):
            return "de"
        if raw.startswith("ko"):
            return "ko"
        # Any other unknown or unsupported locale falls back to English
        return "en"

    @staticmethod
    def _validate_json(data: object) -> list[TranslationEntry] | None:
        """Parse and validate raw JSON data into a list of TranslationEntry."""
        if not isinstance(data, list) or not all(isinstance(entry, dict) for entry in data):
            return None
        entries: list[TranslationEntry] = []
        for entry in cast(list[dict[str, object]], data):
            try:
                entries.append(TranslationEntry.from_dict(entry))
            except (ValueError, TypeError):
                continue
        return entries

    def _load_sync(self, locale: str) -> list[TranslationEntry]:
        """Synchronous translation loader with caching and English fallback."""
        now = time.time()
        cached = self._cache.get(locale)
        if cached and (now - cached[1]) < self._cache_ttl:
            return cached[0]

        result: list[TranslationEntry] = []

        try:
            with open(f"locales/{locale}.json", encoding="utf-8") as file:
                data: object = json.load(file)
                parsed = self._validate_json(data)
                if parsed is not None:
                    result = parsed
                else:
                    print(f"Invalid translation schema for locale '{locale}'.")
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the translation file for locale '{locale}'.")

        # Fallback to English if the requested locale failed and isn't English itself
        if not result and locale != "en":
            en_cached = self._cache.get("en")
            if en_cached and (now - en_cached[1]) < self._cache_ttl:
                result = en_cached[0]
            else:
                try:
                    with open("locales/en.json", encoding="utf-8") as file:
                        fallback_data: object = json.load(file)
                        parsed = self._validate_json(fallback_data)
                        if parsed is not None:
                            self._cache["en"] = (parsed, now)
                            result = parsed
                        else:
                            print("Invalid translation schema for locale 'en'.")
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

        self._cache[locale] = (result, now)
        return result

    def _find_entry(self, entries: list[TranslationEntry], key: str) -> TranslationEntry | None:
        """Search for a translation entry by its identifier (case-insensitive)."""
        lower_key = key.lower()
        for entry in entries:
            if entry.identifier.lower() == lower_key:
                return entry
        return None

    def _report_missing(self, locale_str: str, key: str) -> None:
        """Report a missing translation key to the bot so developers can add it."""
        report_id = (locale_str, key)
        if report_id in reported_missing:
            return
        reported_missing.add(report_id)
        try:
            task = asyncio.create_task(missingLocalization(locale_str, key))

            def _handle_task_exception(t: asyncio.Task[Any]) -> None:
                if t.cancelled():
                    return
                exc = t.exception()
                if exc is not None:
                    print(f"Exception in missingLocalization task for key '{key}' in locale '{locale_str}': {exc}")
                    import traceback

                    traceback.print_exception(type(exc), exc, exc.__traceback__)

            task.add_done_callback(_handle_task_exception)
        except RuntimeError:
            try:
                asyncio.run(missingLocalization(locale_str, key))
            except Exception as e:
                print(f"Exception in missingLocalization for key '{key}' in locale '{locale_str}': {e}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def load_locale(self, locale: str) -> list[TranslationEntry]:
        """Async: load translations for *locale* off the event loop."""
        return await run_blocking(self._load_sync, locale)

    def load_translations(self, locale: str) -> list[TranslationEntry]:
        """Load translations for *locale* (synchronous, cached).

        .. deprecated::
            Use :meth:`load_locale` for async contexts.
        """
        return self._load_sync(locale)

    async def load_translations_async(self, locale: str) -> list[TranslationEntry]:
        """Async wrapper for backward compatibility.

        .. deprecated::
            Use :meth:`load_locale`.
        """
        return await run_blocking(self._load_sync, locale)

    def get_translation(
        self,
        translations: list[TranslationEntry],
        key: str,
    ) -> TranslationEntry | None:
        """Retrieve a translation entry by its identifier (case-insensitive).

        Parameters
        ----------
        translations:
            A list of :class:`TranslationEntry` objects.
        key:
            The translation identifier to look up.

        Returns
        -------
        TranslationEntry | None
            The matching entry, or ``None`` if not found.
        """
        return self._find_entry(translations, key)

    def localize(
        self,
        locale: discord.Locale | str,
        key: str,
        **args: str | int | float,
    ) -> str:
        """Retrieve the localized text for *locale* and substitute placeholders.

        Parameters
        ----------
        locale:
            A :class:`discord.Locale` enum value or a locale string
            (e.g. ``"de"``, ``"en-US"``).
        key:
            The translation identifier to look up.
        **args:
            Template variable values for ``$placeholder`` substitution.

        Returns
        -------
        str
            The formatted translation, or ``"err: no translation found."``
            if the key is missing.
        """
        locale_str = self._normalize_locale(locale)
        translations = self._load_sync(locale_str)
        entry = self._find_entry(translations, key)

        if entry is None:
            print(f"No translation found for key '{key}' in locale '{locale_str}'.")
            self._report_missing(locale_str, key)
            return TRANSLATION_NOT_FOUND

        template = Template(entry.translation)
        return str(template.safe_substitute(args))

    def test_localize(
        self,
        locale: str,
        key: str,
        **args: Any,
    ) -> str:
        """Test-oriented lookup: falls back to German on missing keys."""
        translations = self._load_sync(locale)
        entry = self._find_entry(translations, key)
        if entry is None:
            return self.localize("de", key, **args) if locale != "de" else f"No translation found for key '{key}'."
        template = Template(entry.translation)
        return template.safe_substitute(args)

    def get_available_locales(self) -> list[str]:
        """Return a list of locale identifiers that have cached translations."""
        return list(self._cache.keys())

    def reload_locales(self) -> None:
        """Clear the translation cache so the next load re-reads from disk."""
        self._cache.clear()


# Backward-compatible alias so ``from localizer import tanjunLocalizer``
# continues to work without changes across 120+ import sites.
tanjunLocalizer = LocalizerService()