import json
from string import Template

class Localizer:
    def __init__(self):
        self.translations = {}
    
    def load_translations(self, locale):
        """ Load the translations from a JSON file based on the specified locale. """
        try:
            with open(f"locales/{locale}.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"No translation file found for locale '{locale}'.")
            return {}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the translation file for locale '{locale}'.")
            return {}

    def get_nested_translation(self, translations, key):
        """ Retrieve a nested translation using dot notation for nested keys. """
        keys = key.split('.')
        translation = translations
        for k in keys:
            if k in translation:
                translation = translation[k]
            else:
                return None  # Key does not exist in the nested structure
        return translation

    def localize(self, locale, key, **args):
        """ Retrieve the localized text for the specified locale and format it with any arguments provided. """
        translations = self.load_translations(locale)
        template_string = self.get_nested_translation(translations, key)
        if template_string is None:
            return f"[{key}] not found in {locale} translations."
        template = Template(template_string)
        return template.safe_substitute(args)

tanjunLocalizer = Localizer()