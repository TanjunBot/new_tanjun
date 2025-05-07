# Unused imports:
# from utility import missingLocalization
from __future__ import annotations

import json

import discord
from discord import app_commands

from localizer import tanjunLocalizer


class TanjunTranslator(app_commands.Translator):
    def __init__(self):
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        with open("locales/de.json", encoding="utf-8") as f:
            self.translations = json.load(f)

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext,
    ) -> str | None:
        if locale.value not in ["de", "de-DE", "en", "en-US", "en-GB"]:
            return None

        if locale.value in ["en-US", "en-GB"]:
            locale = "en"

        string = str(string).replace("_", ".")

        current = tanjunLocalizer.localize(locale, string)

        if isinstance(current, str):
            return current
        elif isinstance(current, dict):
            if context.location == app_commands.TranslationContextLocation.command_name:
                return current.get("name")
            elif context.location == app_commands.TranslationContextLocation.command_description:
                return current.get("description")
            elif context.location == app_commands.TranslationContextLocation.parameter_name:
                return current.get("name")
            elif context.location == app_commands.TranslationContextLocation.parameter_description:
                return current.get("description")

        return None
