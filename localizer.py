import asyncio
import json
import time
from string import Template
from typing import Any, cast

from utility import missingLocalization
from utils.async_io import run_blocking

CACHE_TTL: float = 300.0  # 5 minutes

reported_locales: list[str] = []


class Localizer:
    def __init__(self) -> None:
        self.translations: dict[str, list[dict[str, object]]] = {}
        self._cache: dict[str, tuple[list[dict[str, object]], float]] = {}
        self._cache_ttl: float = CACHE_TTL

    def _load_translations_sync(self, locale: str) -> list[dict[str, object]]:
        """Load the translations from a JSON file based on the specified locale.

        Results are cached in memory with a TTL to avoid redundant disk I/O.
        """
        now = time.time()
        cached = self._cache.get(locale)
        if cached and (now - cached[1]) < self._cache_ttl:
            return cached[0]

        def _validate(data: object) -> list[dict[str, object]] | None:
            if isinstance(data, list) and all(isinstance(entry, dict) for entry in data):
                return cast(list[dict[str, object]], data)
            return None

        result: list[dict[str, object]] = []

        try:
            with open(f"locales/{locale}.json", encoding="utf-8") as file:
                data: object = json.load(file)
                parsed = _validate(data)
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
                        parsed = _validate(fallback_data)
                        if parsed is not None:
                            self._cache["en"] = (parsed, now)
                            result = parsed
                        else:
                            print("Invalid translation schema for locale 'en'.")
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

        self._cache[locale] = (result, now)
        return result

    async def load_translations_async(self, locale: str) -> list[dict[str, object]]:
        """Async wrapper: load translations off the event loop via the shared thread pool."""
        return await run_blocking(self._load_translations_sync, locale)

    def load_translations(self, locale: str) -> list[dict[str, object]]:
        return self._load_translations_sync(locale)

    def get_translation(self, translations: list[dict[str, object]], key: str) -> dict[str, object] | None:
        """Retrieve a nested translation using dot notation for nested keys."""
        translation: dict[str, object] | None = next(
            (t for t in translations if str(t.get("identifier", "")).lower() == key.lower()),
            None,
        )

        return translation

    def localize(self, locale: object, key: str, **args: object) -> str:
        """Retrieve the localized text for the specified locale and format it with any arguments provided."""
        locale_str: str = str(locale)
        if locale_str in ["en", "en-US", "en-GB"]:
            locale_str = "en"
        elif locale_str.startswith("de"):
            locale_str = "de"
        translations: list[dict[str, object]] = self.load_translations(locale_str)
        translation: dict[str, object] | None = self.get_translation(translations, key)
        if translation is None:
            print(f"No translation found for key '{key}'.")
            if locale_str not in reported_locales:
                reported_locales.append(locale_str)
                try:
                    asyncio.create_task(missingLocalization(locale_str))
                except RuntimeError:
                    # No running loop — fall back to blocking call
                    pass
            return "err: no translation found."

        template_string: str = str(translation.get("translation", ""))
        template: Template = Template(template_string)
        # safe_substitute expects dict[str, object] which args is now
        return str(template.safe_substitute(args))

    def test_localize(self, locale: str, key: str, **args: Any) -> str:
        translations = self.load_translations(locale)
        translation = self.get_translation(translations, key)
        if translation is None:
            return self.localize("de", key, **args) if locale != "de" else f"No translation found for key '{key}'."
        template_string = str(translation.get("translation", ""))
        template = Template(template_string)
        return template.safe_substitute(args)


tanjunLocalizer = Localizer()
