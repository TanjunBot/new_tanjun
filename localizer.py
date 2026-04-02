import json
from string import Template
from typing import Any, cast, List, Dict, Optional, Union

from utility import missingLocalization

reported_locales: list[str] = []


class Localizer:
    def __init__(self) -> None:
        self.translations: Dict[str, List[Dict[str, object]]] = {}

    def load_translations(self, locale: str) -> List[Dict[str, object]]:
        """Load the translations from a JSON file based on the specified locale."""
        try:
            with open(f"locales/{locale}.json", encoding="utf-8") as file:
                data: object = json.load(file)
                return cast(List[Dict[str, object]], data)
        except FileNotFoundError:
            try:
                with open("locales/en.json", encoding="utf-8") as file:
                    data: object = json.load(file)
                    return cast(List[Dict[str, object]], data)
            except (FileNotFoundError, json.JSONDecodeError):
                return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the translation file for locale '{locale}'.")
            return []

    def get_translation(self, translations: List[Dict[str, object]], key: str) -> Optional[Dict[str, object]]:
        """Retrieve a nested translation using dot notation for nested keys."""
        translation: Optional[Dict[str, object]] = next(
            (t for t in translations if isinstance(t, dict) and str(t.get("identifier", "")).lower() == key.lower()),
            None,
        )

        return translation

    def localize(self, locale: object, key: str, **args: object) -> str:
        """Retrieve the localized text for the specified locale and format it with any arguments provided."""
        locale_str: str = str(locale)
        if locale_str in ["en", "en-US", "en-GB"]:
            locale_str = "en"
        translations: List[Dict[str, object]] = self.load_translations(locale_str)
        translation: Optional[Dict[str, object]] = self.get_translation(translations, key)
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
