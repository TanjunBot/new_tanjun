from __future__ import annotations

import json
from typing import Any, cast

import discord
from discord import app_commands

from localizer import LocalizerService, tanjunLocalizer


class TanjunTranslator(app_commands.Translator):
    """Discord app command translator backed by the bot's LocalizerService.

    Parameters
    ----------
    localizer:
        The :class:`LocalizerService` instance to use for translations.
        Defaults to the global ``tanjunLocalizer``.
    """

    def __init__(self, localizer: LocalizerService | None = None) -> None:
        self._localizer = localizer or tanjunLocalizer
        self.translations: list[dict[str, object]] = []
        self._load_translations()

    def _load_translations(self) -> None:
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
        if str(locale.value) not in ("de", "de-DE", "en", "en-US", "en-GB"):
            return None

        locale_str: str = str(locale.value)
        if locale_str in ("en-US", "en-GB"):
            locale_str = "en"

        key_str: str = str(string).replace("_", ".")

        current = self._localizer.localize(locale, key_str)

        if isinstance(current, str):
            if current == "err: no translation found.":
                return None
            return current

        return None
