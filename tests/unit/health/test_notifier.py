"""Tests for health/notifier.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from health.checks import HealthCheckResult, HealthStatus
from health.notifier import _parse_alert_config, notify_health_failures


class TestParseAlertConfig:
    def test_parses_valid_env(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "123456789")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "987654321")
        channel_id, user_id = _parse_alert_config()
        assert channel_id == 123456789
        assert user_id == 987654321

    def test_missing_channel_raises(self, monkeypatch):
        monkeypatch.delenv("HEALTH_ALERT_CHANNEL_ID", raising=False)
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "1")
        with pytest.raises(RuntimeError, match="HEALTH_ALERT_CHANNEL_ID"):
            _parse_alert_config()

    def test_missing_user_raises(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "1")
        monkeypatch.delenv("HEALTH_ALERT_USER_ID", raising=False)
        with pytest.raises(RuntimeError, match="HEALTH_ALERT_USER_ID"):
            _parse_alert_config()

    def test_invalid_channel_id_raises(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "not-int")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "1")
        with pytest.raises(RuntimeError, match="must be an integer"):
            _parse_alert_config()

    def test_invalid_user_id_raises(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "1")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "bad")
        with pytest.raises(RuntimeError, match="must be an integer"):
            _parse_alert_config()


class TestNotifyHealthFailures:
    @pytest.mark.asyncio
    async def test_empty_failures_is_noop(self):
        bot = MagicMock()
        await notify_health_failures(bot, [])

    @pytest.mark.asyncio
    async def test_sends_embed_to_cached_channel(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        channel = MagicMock()
        channel.send = AsyncMock()
        bot = MagicMock()
        bot.get_channel.return_value = channel
        failures = [
            HealthCheckResult("DB", HealthStatus.CRITICAL, "down"),
            HealthCheckResult("API", HealthStatus.DEGRADED, "slow"),
        ]
        await notify_health_failures(bot, failures)
        channel.send.assert_awaited_once()
        call_kwargs = channel.send.await_args.kwargs
        assert call_kwargs["content"] == "<@222>"

    @pytest.mark.asyncio
    async def test_fetches_channel_when_not_cached(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        channel = MagicMock()
        channel.send = AsyncMock()
        bot = MagicMock()
        bot.get_channel.return_value = None
        bot.fetch_channel = AsyncMock(return_value=channel)
        failures = [HealthCheckResult("DB", HealthStatus.CRITICAL, "down")]
        await notify_health_failures(bot, failures)
        bot.fetch_channel.assert_awaited_once_with(111)
        channel.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_channel_not_found_logs_warning(self, monkeypatch):
        import discord

        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        bot = MagicMock()
        bot.get_channel.return_value = None
        bot.fetch_channel = AsyncMock(side_effect=discord.NotFound(MagicMock(), "missing"))
        failures = [HealthCheckResult("DB", HealthStatus.CRITICAL, "down")]
        with patch("health.notifier.logger") as log:
            await notify_health_failures(bot, failures)
        log.warning.assert_called()

    @pytest.mark.asyncio
    async def test_channel_without_send_skips(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        channel = object()
        bot = MagicMock()
        bot.get_channel.return_value = channel
        failures = [HealthCheckResult("DB", HealthStatus.CRITICAL, "down")]
        with patch("health.notifier.logger") as log:
            await notify_health_failures(bot, failures)
        log.warning.assert_called()

    @pytest.mark.asyncio
    async def test_chunks_large_failure_lists(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        channel = MagicMock()
        channel.send = AsyncMock()
        bot = MagicMock()
        bot.get_channel.return_value = channel
        failures = [HealthCheckResult(f"Check{i}", HealthStatus.CRITICAL, f"msg{i}") for i in range(30)]
        await notify_health_failures(bot, failures)
        assert channel.send.await_count == 2

    @pytest.mark.asyncio
    async def test_send_exception_logged(self, monkeypatch):
        monkeypatch.setenv("HEALTH_ALERT_CHANNEL_ID", "111")
        monkeypatch.setenv("HEALTH_ALERT_USER_ID", "222")
        channel = MagicMock()
        channel.send = AsyncMock(side_effect=RuntimeError("send failed"))
        bot = MagicMock()
        bot.get_channel.return_value = channel
        failures = [HealthCheckResult("DB", HealthStatus.CRITICAL, "down")]
        with patch("health.notifier.logger") as log:
            await notify_health_failures(bot, failures)
        log.error.assert_called()
