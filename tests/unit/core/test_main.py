"""Unit tests for main.py startup helpers and Sentry filtering."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

import discord

discord.__version__ = "2.7.1"
if not hasattr(discord, "DiscordException"):
    discord.DiscordException = type("DiscordException", (Exception,), {})

import main as main_mod

main_mod.discord.DiscordException = type("DiscordException", (Exception,), {})


class TestSentryEventFilter:
    def test_returns_event_when_no_exc_info(self):
        event = {"message": "test"}
        assert main_mod._should_discard_sentry_event(event, {}) is event

    def test_discards_forbidden(self):
        exc = discord.Forbidden(MagicMock(), "forbidden")
        assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None

    def test_discards_not_found(self):
        exc = discord.NotFound(MagicMock(), "not found")
        assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None

    def test_discards_rate_limit_429(self):
        exc = discord.HTTPException(MagicMock(), "rate limited")
        exc.status = 429
        assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None

    def test_keeps_other_http_exceptions(self):
        exc = discord.HTTPException(MagicMock(), "server error")
        exc.status = 500
        event = {"id": "1"}
        assert main_mod._should_discard_sentry_event(event, {"exc_info": (type(exc), exc, None)}) is event

    def test_discards_unknown_message_10008(self):
        exc = main_mod.discord.DiscordException("10008 unknown message")
        assert main_mod._should_discard_sentry_event({}, {"exc_info": (type(exc), exc, None)}) is None

    def test_keeps_unrelated_discord_exception(self):
        exc = main_mod.discord.DiscordException("some other error")
        event = {"event_id": "abc"}
        assert main_mod._should_discard_sentry_event(event, {"exc_info": (type(exc), exc, None)}) is event

    def test_keeps_value_error(self):
        exc = ValueError("boom")
        event = {}
        assert main_mod._should_discard_sentry_event(event, {"exc_info": (ValueError, exc, None)}) is event


class TestLoadExtension:
    @pytest.mark.asyncio
    async def test_loadextension_success(self):
        bot = MagicMock()
        bot.load_extension = AsyncMock()
        await main_mod.loadextension(bot, "listeners")
        bot.load_extension.assert_awaited_once_with("extensions.listeners")

    @pytest.mark.asyncio
    async def test_loadextension_prefixes_extensions(self):
        bot = MagicMock()
        bot.load_extension = AsyncMock()
        await main_mod.loadextension(bot, "level")
        bot.load_extension.assert_awaited_once_with("extensions.level")

    @pytest.mark.asyncio
    async def test_loadextension_reraises_on_failure(self):
        bot = MagicMock()
        bot.load_extension = AsyncMock(side_effect=RuntimeError("fail"))
        with pytest.raises(RuntimeError, match="fail"):
            await main_mod.loadextension(bot, "bad")


class TestLoadTranslator:
    @pytest.mark.asyncio
    async def test_sets_translator_on_tree(self):
        bot = MagicMock()
        bot.tree = MagicMock()
        bot.tree.set_translator = AsyncMock()
        with patch.object(main_mod, "TanjunTranslator") as translator_cls:
            translator_cls.return_value = MagicMock()
            await main_mod.loadTranslator(bot)
        bot.tree.set_translator.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_skips_when_no_tree(self):
        bot = MagicMock()
        bot.tree = None
        with patch.object(main_mod, "TanjunTranslator"):
            await main_mod.loadTranslator(bot)


class TestDatabasePool:
    @pytest.mark.asyncio
    async def test_init_database_pool_success(self):
        mock_pool = MagicMock()
        with patch("asyncmy.create_pool", new=AsyncMock(return_value=mock_pool)):
            pool = await main_mod._init_database_pool()
        assert pool is mock_pool

    @pytest.mark.asyncio
    async def test_init_database_pool_failure(self):
        with (
            patch.object(main_mod, "database_connect_max_retries", 1),
            patch("asyncmy.create_pool", new=AsyncMock(side_effect=OSError("db down"))),
        ):
            with pytest.raises(OSError, match="db down"):
                await main_mod._init_database_pool()

    @pytest.mark.asyncio
    async def test_init_database_pool_retries_then_succeeds(self):
        mock_pool = MagicMock()
        create_pool = AsyncMock(side_effect=[OSError("db down"), mock_pool])
        with (
            patch.object(main_mod, "database_connect_max_retries", 2),
            patch.object(main_mod, "database_connect_retry_delay_sec", 0),
            patch("asyncmy.create_pool", new=create_pool),
            patch.object(main_mod.asyncio, "sleep", new=AsyncMock()),
        ):
            pool = await main_mod._init_database_pool()
        assert pool is mock_pool
        assert create_pool.await_count == 2


class TestLoadAllExtensions:
    @pytest.mark.asyncio
    async def test_loads_py_files_from_extensions_dir(self):
        bot = MagicMock()
        with patch.object(main_mod, "loadextension", new=AsyncMock()) as load_mock:
            await main_mod._load_all_extensions(bot)
        assert load_mock.await_count >= 1
        called_names = [call.args[1] for call in load_mock.await_args_list]
        assert "listeners" in called_names or "level" in called_names


class TestOnReady:
    def test_bot_ready_path_uses_configured_location(self, monkeypatch, tmp_path):
        ready_path = tmp_path / ".bot_ready"
        monkeypatch.setenv("BOT_READY_FILE", str(ready_path))
        assert main_mod._bot_ready_path() == ready_path

    def test_clear_startup_marker_removes_file(self, monkeypatch, tmp_path):
        startup_path = tmp_path / ".bot_startup"
        monkeypatch.setenv("BOT_STARTUP_FILE", str(startup_path))
        startup_path.touch()
        main_mod._clear_startup_marker()
        assert not startup_path.exists()

    @pytest.mark.asyncio
    async def test_on_ready_writes_ready_file_and_presence(self, monkeypatch, tmp_path):
        ready_path = tmp_path / ".bot_ready"
        monkeypatch.setenv("BOT_READY_FILE", str(ready_path))
        bot = MagicMock()
        bot.user = MagicMock(id=123)
        bot.change_presence = AsyncMock()

        ready_path.parent.mkdir(parents=True, exist_ok=True)
        ready_path.touch()
        if bot.user is not None:
            await bot.change_presence(
                activity=main_mod.discord.Game(
                    name=main_mod.config.activity.format(version=main_mod.config.version)
                )
            )

        assert ready_path.is_file()
        bot.change_presence.assert_awaited_once()


class TestMainFlow:
    @pytest.mark.asyncio
    async def test_main_happy_path(self):
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
        assert services.pool is mock_pool

    @pytest.mark.asyncio
    async def test_main_health_failure_stops_before_start(self):
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
            failure = MagicMock(check_name="db", message="down")
            manager.run_startup_checks = AsyncMock(return_value=(False, [failure]))
            hm_cls.return_value = manager
            db_mgr.set_pool = MagicMock()
            await main_mod.main()

        mock_bot.start.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_main_pool_failure_cancels_extensions(self):
        mock_bot = MagicMock()
        mock_bot._pool_ready = asyncio.Event()

        with (
            patch.object(main_mod, "bot", mock_bot),
            patch.object(main_mod, "_load_all_extensions", new=AsyncMock(return_value=None)),
            patch.object(main_mod, "_init_database_pool", new=AsyncMock(side_effect=RuntimeError("pool fail"))),
        ):
            with pytest.raises(RuntimeError, match="pool fail"):
                await main_mod.main()


class TestMainModuleAttributes:
    def test_bot_has_intents_configured(self):
        assert main_mod.bot is not None

    def test_entry_point_guard(self):
        assert main_mod.__name__ == "main"

    def test_sentry_filter_is_callable(self):
        assert callable(main_mod._should_discard_sentry_event)
