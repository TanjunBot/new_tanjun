from __future__ import annotations

import discord


class LocalizedString:
    __slots__ = ("_key",)

    def __init__(self, key: str) -> None:
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    @property
    def discord_key(self) -> str:
        return self._key.replace(".", "_")

    def __call__(
        self,
        locale: discord.Locale | str,
        /,
        **kwargs: str | int | float,
    ) -> str:
        from string import Template

        from localizer import TRANSLATION_NOT_FOUND, tanjunLocalizer

        if "locale" not in kwargs:
            return tanjunLocalizer.localize(locale, self._key, **kwargs)
        locale_ph = kwargs.pop("locale")
        locale_str = tanjunLocalizer._normalize_locale(locale)
        translations = tanjunLocalizer._load_sync(locale_str)
        entry = tanjunLocalizer._find_entry(translations, self._key)
        if entry is None:
            tanjunLocalizer.localize(locale, self._key)
            return TRANSLATION_NOT_FOUND
        subs = {**kwargs, "locale": locale_ph}
        return str(Template(entry.translation).safe_substitute(subs))

    def __repr__(self) -> str:
        return f"LocalizedString({self._key!r})"


class ResolveMap:
    __slots__ = ("_prefix", "_suffixes")

    def __init__(self, prefix: str, suffixes: dict[str, LocalizedString]) -> None:
        self._prefix = prefix
        self._suffixes = suffixes

    def resolve(self, suffix: str) -> LocalizedString:
        if suffix in self._suffixes:
            return self._suffixes[suffix]
        return LocalizedString(f"{self._prefix}{suffix}")

    def __call__(self, suffix: str) -> LocalizedString:
        return self.resolve(suffix)
