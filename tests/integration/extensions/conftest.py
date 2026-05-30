from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest

from tests.helpers.extension_loader import (
    fire_cog_on_ready,
    load_extension,
    make_bot_for_extensions,
)


def _ensure_app_command_errors() -> None:
    mock = sys.modules.get("discord")
    if mock is None:
        return

    class AppCommandError(Exception):
        pass

    class CommandOnCooldown(AppCommandError):
        def __init__(self, *args, retry_after: float = 0, **kwargs) -> None:
            super().__init__(*args)
            self.retry_after = retry_after

    class CheckFailure(AppCommandError):
        pass

    class MissingPermissions(CheckFailure):
        def __init__(self, missing_permissions: list[str] | None = None) -> None:
            self.missing_permissions = missing_permissions or []

    class BotMissingPermissions(CheckFailure):
        def __init__(self, missing_permissions: list[str] | None = None) -> None:
            self.missing_permissions = missing_permissions or []

    class CommandInvokeError(AppCommandError):
        def __init__(self, original: Exception) -> None:
            self.original = original

    class CommandNotFound(AppCommandError):
        pass

    class TransformerError(AppCommandError):
        pass

    ac = mock.app_commands
    ac.AppCommandError = AppCommandError
    ac.CommandOnCooldown = CommandOnCooldown
    ac.CheckFailure = CheckFailure
    ac.MissingPermissions = MissingPermissions
    ac.BotMissingPermissions = BotMissingPermissions
    ac.CommandInvokeError = CommandInvokeError
    ac.CommandNotFound = CommandNotFound
    ac.TransformerError = TransformerError
    ac.AppCommandOptionType = MagicMock()
    ac.AppCommandOptionType.string = "string"
    ac.autocomplete = lambda *a, **k: (lambda f: f)

    mock.ext.commands.CommandInvokeError = CommandInvokeError


@pytest.fixture(scope="session", autouse=True)
def _real_discord_app_command_errors():
    _ensure_app_command_errors()


@pytest.fixture
def extension_bot() -> MagicMock:
    return make_bot_for_extensions()


async def load_extension_bot(extension: str, *, fire_ready: bool = True) -> MagicMock:
    bot = make_bot_for_extensions()
    await load_extension(bot, extension)
    if fire_ready:
        await fire_cog_on_ready(bot)
    return bot
