import json
from string import Template
from typing import Any, cast

from utility import missingLocalization
from utils.async_io import run_blocking

reported_locales: list[str] = []


class Localizer:
    def __init__(self) -> None:
        self.translations: dict[str, list[dict[str, object]]] = {}

    def _load_translations_sync(self, locale: str) -> list[dict[str, object]]:
        """Load the translations from a JSON file based on the specified locale."""
        def _validate(data: object) -> list[dict[str, object]] | None:
            if isinstance(data, list) and all(isinstance(entry, dict) for entry in data):
                return cast(list[dict[str, object]], data)
            return None

        try:
            with open(f"locales/{locale}.json", encoding="utf-8") as file:
                data: object = json.load(file)
                result = _validate(data)
                if result is not None:
                    return result
                print(f"Invalid translation schema for locale '{locale}'.")
        except FileNotFoundError:
            pass
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the translation file for locale '{locale}'.")
            return []

        # Fallback to English
        try:
            with open("locales/en.json", encoding="utf-8") as file:
                fallback_data: object = json.load(file)
                result = _validate(fallback_data)
                if result is not None:
                    return result
                print("Invalid translation schema for locale 'en'.")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return []

    async def load_translations_async(self, locale: str) -> list[dict[str, object]]:
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
        translations: list[dict[str, object]] = self.load_translations(locale_str)
        translation: dict[str, object] | None = self.get_translation(translations, key)
        if translation is None:
            print(f"No translation found for key '{key}'.")
            if locale_str not in reported_locales:
                reported_locales.append(locale_str)
                missingLocalization(key)
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
