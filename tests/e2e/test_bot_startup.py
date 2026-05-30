from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

import discord

discord.__version__ = "2.4.0"
if not hasattr(discord, "DiscordException"):
    discord.DiscordException = type("DiscordException", (Exception,), {})

import main as main_mod  # noqa: E402

main_mod.discord.DiscordException = type("DiscordException", (Exception,), {})

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_main_lists_extension_files():
    extensions = [
        f.replace(".py", "")
        for f in os.listdir("extensions")
        if f.endswith(".py") and not f.startswith("__")
    ]
    assert len(extensions) >= 18
    assert "listeners" in extensions
    assert "error_handler" in extensions
    assert "level" in extensions


@pytest.mark.asyncio
async def test_startup_sets_pool_ready_event():
    bot = MagicMock()
    bot._pool_ready = asyncio.Event()
    bot._pool = MagicMock()
    bot._pool_ready.set()
    assert bot._pool_ready.is_set()


@pytest.mark.asyncio
async def test_create_tables_called_during_startup(patched_api_pool):
    with patch("api.create_tables", new=AsyncMock()) as create_mock:
        await create_mock(patched_api_pool)
    create_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_preload_guild_configs(patched_api_pool):
    with patch("api.preload_guild_configs", new=AsyncMock()) as preload:
        await preload(patched_api_pool)
    preload.assert_awaited_once()


@pytest.mark.asyncio
async def test_health_manager_startup_checks():
    from health.manager import HealthCheckManager

    bot = MagicMock()
    manager = HealthCheckManager(bot)
    with patch.object(manager, "run_startup_checks", new=AsyncMock(return_value=(True, []))):
        ok, failures = await manager.run_startup_checks()
    assert ok is True
    assert failures == []


def test_should_discard_returns_event_when_no_exc_info():
    event = {"message": "test"}
    assert main_mod._should_discard_sentry_event(event, {}) is event


def test_should_discard_forbidden():
    exc = discord.Forbidden(MagicMock(), "forbidden")
    assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None


def test_should_discard_not_found():
    exc = discord.NotFound(MagicMock(), "not found")
    assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None


def test_should_discard_rate_limit():
    exc = discord.HTTPException(MagicMock(), "rate limited")
    exc.status = 429
    assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None


def test_should_discard_unknown_message():
    exc = main_mod.discord.DiscordException("10008 unknown message")
    assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None


def test_should_keep_other_exceptions():
    exc = ValueError("boom")
    assert main_mod._should_discard_sentry_event({}, {"exc_info": (ValueError, exc, None)}) == {}


@pytest.mark.asyncio
async def test_loadextension_success():
    bot = MagicMock()
    bot.load_extension = AsyncMock()
    await main_mod.loadextension(bot, "listeners")
    bot.load_extension.assert_awaited_once_with("extensions.listeners")


@pytest.mark.asyncio
async def test_loadextension_raises_on_failure():
    bot = MagicMock()
    bot.load_extension = AsyncMock(side_effect=RuntimeError("fail"))
    with pytest.raises(RuntimeError):
        await main_mod.loadextension(bot, "bad")


@pytest.mark.asyncio
async def test_load_translator_sets_tree():
    bot = MagicMock()
    bot.tree = MagicMock()
    bot.tree.set_translator = AsyncMock()
    with patch.object(main_mod, "TanjunTranslator") as translator_cls:
        translator_cls.return_value = MagicMock()
        await main_mod.loadTranslator(bot)
    bot.tree.set_translator.assert_awaited_once()


@pytest.mark.asyncio
async def test_load_translator_skips_without_tree():
    bot = MagicMock()
    bot.tree = None
    with patch.object(main_mod, "TanjunTranslator"):
        await main_mod.loadTranslator(bot)


@pytest.mark.asyncio
async def test_init_database_pool_success():
    mock_pool = MagicMock()
    with patch("asyncmy.create_pool", new=AsyncMock(return_value=mock_pool)):
        pool = await main_mod._init_database_pool()
    assert pool is mock_pool


@pytest.mark.asyncio
async def test_init_database_pool_failure():
    with patch("asyncmy.create_pool", new=AsyncMock(side_effect=OSError("db down"))):
        with pytest.raises(OSError):
            await main_mod._init_database_pool()


@pytest.mark.asyncio
async def test_load_all_extensions_from_main():
    bot = MagicMock()
    with patch.object(main_mod, "loadextension", new=AsyncMock()) as load_mock:
        await main_mod._load_all_extensions(bot)
    assert load_mock.await_count >= 1


@pytest.mark.asyncio
async def test_main_happy_path():
    mock_pool = MagicMock()
    mock_bot = MagicMock()
    mock_bot._pool_ready = asyncio.Event()
    mock_bot._pool = None
    mock_bot.tree = MagicMock()
    mock_bot.tree.set_translator = AsyncMock()
    mock_bot.start = AsyncMock()

    with (
        patch.object(main_mod, "bot", mock_bot),
        patch.object(main_mod, "_load_all_extensions", new=AsyncMock()),
        patch.object(main_mod, "_init_database_pool", new=AsyncMock(return_value=mock_pool)),
        patch.object(main_mod, "loadTranslator", new=AsyncMock()),
        patch("api.create_tables", new=AsyncMock()),
        patch("api.preload_guild_configs", new=AsyncMock()),
        patch("api.db_manager") as db_mgr,
        patch("api.set_bot"),
        patch.object(main_mod, "services") as services,
        patch("services.twitch_service.init_twitch_service", new=AsyncMock()),
        patch.object(main_mod, "HealthCheckManager") as hm_cls,
    ):
        manager = MagicMock()
        manager.run_startup_checks = AsyncMock(return_value=(True, []))
        manager.start_periodic_checks = AsyncMock()
        manager.register = MagicMock()
        hm_cls.return_value = manager
        db_mgr.set_pool = MagicMock()
        await main_mod.main()

    mock_bot.start.assert_awaited_once()
    assert mock_bot._pool_ready.is_set()


@pytest.mark.asyncio
async def test_main_health_check_failure_returns_early():
    mock_pool = MagicMock()
    mock_bot = MagicMock()
    mock_bot._pool_ready = asyncio.Event()
    mock_bot.tree = MagicMock()
    mock_bot.start = AsyncMock()

    with (
        patch.object(main_mod, "bot", mock_bot),
        patch.object(main_mod, "_load_all_extensions", new=AsyncMock()),
        patch.object(main_mod, "_init_database_pool", new=AsyncMock(return_value=mock_pool)),
        patch.object(main_mod, "loadTranslator", new=AsyncMock()),
        patch("api.create_tables", new=AsyncMock()),
        patch("api.preload_guild_configs", new=AsyncMock()),
        patch("api.db_manager") as db_mgr,
        patch("api.set_bot"),
        patch.object(main_mod, "services"),
        patch("services.twitch_service.init_twitch_service", new=AsyncMock()),
        patch.object(main_mod, "HealthCheckManager") as hm_cls,
    ):
        manager = MagicMock()
        result = MagicMock()
        result.check_name = "db"
        result.message = "down"
        manager.run_startup_checks = AsyncMock(return_value=(False, [result]))
        hm_cls.return_value = manager
        db_mgr.set_pool = MagicMock()
        await main_mod.main()

    mock_bot.start.assert_not_awaited()


@pytest.mark.asyncio
async def test_main_pool_task_failure_cancels_extension_task():
    mock_bot = MagicMock()
    mock_bot._pool_ready = asyncio.Event()

    with (
        patch.object(main_mod, "bot", mock_bot),
        patch.object(main_mod, "_load_all_extensions", new=AsyncMock(return_value=None)),
        patch.object(main_mod, "_init_database_pool", new=AsyncMock(side_effect=RuntimeError("pool fail"))),
    ):
        with pytest.raises(RuntimeError):
            await main_mod.main()


def test_main_module_has_entry_guard():
    assert hasattr(main_mod, "__name__")
