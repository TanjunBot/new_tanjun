from __future__ import annotations

import sys
from collections.abc import AsyncIterator, Iterator
from unittest.mock import MagicMock

import pytest

from tests.helpers.db import make_mock_pool
from tests.helpers.extension_loader import (
    EXTENSION_NAMES,
    fire_cog_on_ready,
    load_all_extensions,
    load_extension,
    make_bot_for_extensions,
)

pytestmark = pytest.mark.e2e


def _make_cog(cog_cls, bot):
    cog = object.__new__(cog_cls)
    cog.bot = bot
    return cog


def _ensure_app_command_errors() -> None:
    mock = sys.modules.get("discord")
    if mock is None:
        return

    class CommandOnCooldown(Exception):
        def __init__(self, *args, retry_after: float = 0, **kwargs) -> None:
            super().__init__(*args)
            self.retry_after = retry_after

    class CheckFailure(Exception):
        pass

    class MissingPermissions(CheckFailure):
        def __init__(self, missing_permissions: list[str] | None = None) -> None:
            self.missing_permissions = missing_permissions or []

    class BotMissingPermissions(CheckFailure):
        def __init__(self, missing_permissions: list[str] | None = None) -> None:
            self.missing_permissions = missing_permissions or []

    class CommandInvokeError(Exception):
        def __init__(self, original: Exception) -> None:
            self.original = original

    class CommandNotFound(Exception):
        pass

    class TransformerError(Exception):
        pass

    ac = mock.app_commands
    ac.CommandOnCooldown = CommandOnCooldown
    ac.CheckFailure = CheckFailure
    ac.MissingPermissions = MissingPermissions
    ac.BotMissingPermissions = BotMissingPermissions
    ac.CommandInvokeError = CommandInvokeError
    ac.CommandNotFound = CommandNotFound
    ac.TransformerError = TransformerError
    mock.ext.commands.CommandInvokeError = CommandInvokeError


def _ensure_discord_cog_listener_fn() -> None:
    mock = sys.modules.get("discord")
    if mock is None:
        return
    mock.Locale = type("Locale", (), {})
    mock.Embed = MagicMock()
    cog = mock.ext.commands.Cog
    if isinstance(cog, type) and not hasattr(cog, "listener"):
        cog.listener = staticmethod(lambda *a, **k: lambda f: f)


@pytest.fixture(scope="session", autouse=True)
def _real_discord_app_command_errors():
    _ensure_app_command_errors()


@pytest.fixture(autouse=True)
def _refresh_app_command_errors():
    _ensure_app_command_errors()


@pytest.fixture(autouse=True)
def _ensure_discord_cog_listener():
    _ensure_discord_cog_listener_fn()


@pytest.fixture(autouse=True)
def reset_api_bot() -> Iterator[None]:
    from api import set_bot

    set_bot(None)
    yield
    set_bot(None)


@pytest.fixture
def e2e_bot():
    from discord.ext import commands

    if not isinstance(commands.Cog, type):
        commands.Cog = type("Cog", (), {"__init__": lambda self, bot=None: setattr(self, "bot", bot)})

    pool, _, _ = make_mock_pool()
    bot = make_bot_for_extensions(pool)
    bot.tree.on_error = None
    return bot


@pytest.fixture
def extension_bot():
    pool, _, _ = make_mock_pool()
    return make_bot_for_extensions(pool)


@pytest.fixture
async def all_extensions_bot(extension_bot) -> AsyncIterator[MagicMock]:
    await load_all_extensions(extension_bot)
    await fire_cog_on_ready(extension_bot)
    yield extension_bot


@pytest.fixture
def listener_cog(e2e_bot):
    import importlib

    import extensions.listeners as listeners_mod

    _ensure_discord_cog_listener_fn()
    importlib.reload(listeners_mod)
    return _make_cog(listeners_mod.ListenerCog, e2e_bot)


@pytest.fixture
def error_cog(e2e_bot):
    import importlib

    import extensions.error_handler as error_mod

    _ensure_discord_cog_listener_fn()
    _ensure_app_command_errors()
    importlib.reload(error_mod)
    return _make_cog(error_mod.ErrorHandlerCog, e2e_bot)


@pytest.fixture
def patched_api_pool(e2e_bot):
    from api import set_bot

    set_bot(e2e_bot)
    return e2e_bot


async def load_extension_bot(extension: str, *, fire_ready: bool = True) -> MagicMock:
    pool, _, _ = make_mock_pool()
    bot = make_bot_for_extensions(pool)
    await load_extension(bot, extension)
    if fire_ready:
        await fire_cog_on_ready(bot)
    return bot


@pytest.fixture(params=EXTENSION_NAMES)
def extension_name(request: pytest.FixtureRequest) -> str:
    return request.param
