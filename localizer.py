import json
from string import Template
from utility import missingLocalization

reported_locales = []


class Localizer:
    def __init__(self):
        self.translations = {}

    def load_translations(self, locale):
        """Load the translations from a JSON file based on the specified locale."""
        try:
            with open(f"locales/{locale}.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            with open("locales/en.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(
                f"Error decoding JSON from the translation file for locale '{locale}'."
            )
            return {}

    def get_translation(self, translations, key):
        """Retrieve a nested translation using dot notation for nested keys."""
        translation = next(
            (
                translation
                for translation in translations
                if translation["identifier"].lower() == key.lower()
            ),
            None,
        )

        return translation

    def localize(self, locale, key, **args):
        """Retrieve the localized text for the specified locale and format it with any arguments provided."""
        if locale in ["en", "en-US", "en-GB"]:
            locale = "en"
        translations = self.load_translations(locale)
        translation = self.get_translation(translations, key)
        if translation is None:
            print(f"No translation found for key '{key}'.")
            if locale not in reported_locales:
                reported_locales.append(locale)
                missingLocalization(key)
            return "err: no translation found."

        template_string = translation["translation"]
        template = Template(template_string)
        return template.safe_substitute(args)

    def test_localize(self, locale, key, **args):
        translations = self.load_translations(locale)
        template_string = self.get_translation(translations, key)
        if template_string is None:
            return (
                self.localize("de", key, **args)
                if locale != "de"
                else f"No translation found for key '{key}'."
            )
        template = Template(template_string)
        return template.safe_substitute(args)


tanjunLocalizer = Localizer()
