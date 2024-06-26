from __future__ import annotations
import discord
from discord import app_commands
import json


class TanjunTranslator(app_commands.Translator):
    def __init__(self):
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        with open('locales/de.json', 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str | None:
        if locale.value not in ['de', 'de-DE']:
            return None

        path = string.message.split('_')
        current = self.translations
        for part in path:
            if part in current:
                current = current[part]
            else:
                return None

        if isinstance(current, str):
            return current
        elif isinstance(current, dict):
            if context.location == app_commands.TranslationContextLocation.command_name:
                return current.get('name')
            elif context.location == app_commands.TranslationContextLocation.command_description:
                return current.get('description')
            elif context.location == app_commands.TranslationContextLocation.parameter_name:
                return current.get('name')
            elif context.location == app_commands.TranslationContextLocation.parameter_description:
                return current.get('description')

        return None
