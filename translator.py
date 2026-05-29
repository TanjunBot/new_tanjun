from __future__ import annotations

from typing import Any

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

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: discord.Locale,
        context: app_commands.TranslationContext[Any, Any],
    ) -> str | None:
        key_str: str = str(string).replace("_", ".")

        current = self._localizer.localize(locale, key_str)

        if current == "err: no translation found.":
            return None
        return current
