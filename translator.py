from __future__ import annotations

import re
from typing import Any

import discord
from discord import app_commands

from localizer import TRANSLATION_NOT_FOUND, LocalizerService, tanjunLocalizer

_DISCORD_NAME_LOCATION_NAMES = frozenset({"command_name", "group_name", "parameter_name"})


def _normalize_discord_command_name(name: str) -> str | None:
    normalized = re.sub(r"\s+", "_", name.strip().lower())
    if not normalized:
        return None
    return normalized[:32]


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

        if current == TRANSLATION_NOT_FOUND:
            return None

        location_name = getattr(context.location, "name", None)
        if location_name in _DISCORD_NAME_LOCATION_NAMES:
            current = _normalize_discord_command_name(current)
            if current is None:
                return None

        return current
