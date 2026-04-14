from __future__ import annotations

import json
from typing import Any, cast

import discord
from discord import app_commands

from localizer import tanjunLocalizer


class TanjunTranslator(app_commands.Translator):
    def __init__(self) -> None:
        self.translations: list[dict[str, object]] = []
        self.load_translations()

    def load_translations(self) -> None:
        try:
            with open("locales/de.json", encoding="utf-8") as f:
                data: object = json.load(f)
                self.translations = cast(list[dict[str, object]], data)
        except (FileNotFoundError, json.JSONDecodeError):
            self.translations = []

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext[Any, Any],
    ) -> str | None:
        if str(locale.value) not in ["de", "de-DE", "en", "en-US", "en-GB"]:
            return None

        locale_str: str = str(locale.value)
        if locale_str in ["en-US", "en-GB"]:
            locale_str = "en"

        key_str: str = str(string).replace("_", ".")

        current: object = tanjunLocalizer.localize(locale_str, key_str)

        if isinstance(current, str):
            if current == "err: no translation found.":
                return None
            return current

        return None
