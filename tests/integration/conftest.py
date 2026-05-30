from __future__ import annotations

import pytest

from tests.helpers.discord import _ensure_discord_types

_ensure_discord_types()


def pytest_configure(config: pytest.Config) -> None:
    import discord

    def _choice(**kwargs: object) -> object:
        return type("Choice", (), kwargs)()

    discord.app_commands.Choice = _choice  # type: ignore[attr-defined]
    _ensure_discord_types()


@pytest.fixture(autouse=True)
def _reset_discord_types() -> None:
    _ensure_discord_types()
    import discord

    def _choice(**kwargs: object) -> object:
        return type("Choice", (), kwargs)()

    discord.app_commands.Choice = _choice  # type: ignore[attr-defined]
