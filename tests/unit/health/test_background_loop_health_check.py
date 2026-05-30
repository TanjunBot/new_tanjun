"""Tests for extensions/health_check.py BackgroundLoopHealthCheck."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from extensions.health_check import BackgroundLoopHealthCheck
from health.checks import HealthStatus


def _running_task():
    task = MagicMock()
    task.is_running = MagicMock(return_value=True)
    return task


def _stopped_task():
    task = MagicMock()
    task.is_running = MagicMock(return_value=False)
    return task


class TestBackgroundLoopHealthCheck:
    @pytest.fixture
    def bot(self):
        return MagicMock()

    def test_name_and_critical(self, bot):
        check = BackgroundLoopHealthCheck(bot)
        assert check.name == "Background Loops"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_critical_when_loop_cog_missing(self, bot):
        bot.get_cog.return_value = None
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.CRITICAL
        assert "LoopCog not found" in result.message

    @pytest.mark.asyncio
    async def test_healthy_when_all_loops_running(self, bot):
        cog = MagicMock()
        for attr in [
            "sendSendReadyGiveaways",
            "endGiveawaysLoop",
            "checkVoiceUsers",
            "addVoiceUserLoop",
            "refillAiTokenLoop",
            "pingServerLoop",
            "backupDatabaseLoop",
            "removeExpiredClaimedBoosterRoles",
            "removeExpiredClaimedBoosterChannels",
            "sendScheduledMessages",
            "pollTwitchStreams",
            "clearNotifiedUsersLoop",
            "sendPokemonWerbung",
        ]:
            setattr(cog, attr, _running_task())
        bot.get_cog.return_value = cog
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.HEALTHY
        assert "13" in result.message

    @pytest.mark.asyncio
    async def test_degraded_when_loop_stopped(self, bot):
        cog = MagicMock()
        for attr in [
            "sendSendReadyGiveaways",
            "endGiveawaysLoop",
            "checkVoiceUsers",
            "addVoiceUserLoop",
            "refillAiTokenLoop",
            "pingServerLoop",
            "backupDatabaseLoop",
            "removeExpiredClaimedBoosterRoles",
            "removeExpiredClaimedBoosterChannels",
            "sendScheduledMessages",
            "pollTwitchStreams",
            "clearNotifiedUsersLoop",
            "sendPokemonWerbung",
        ]:
            setattr(cog, attr, _running_task())
        cog.pingServerLoop = _stopped_task()
        bot.get_cog.return_value = cog
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.DEGRADED
        assert "Ping Server" in result.message
        assert result.details["failed_loops"]

    @pytest.mark.asyncio
    async def test_degraded_when_loop_attribute_missing(self, bot):
        cog = MagicMock(spec=[])
        bot.get_cog.return_value = cog
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.DEGRADED
        assert "missing" in result.message

    @pytest.mark.asyncio
    async def test_degraded_when_is_running_not_callable(self, bot):
        cog = MagicMock()
        bad_task = MagicMock()
        bad_task.is_running = "not-callable"
        cog.sendSendReadyGiveaways = bad_task
        for attr in [
            "endGiveawaysLoop",
            "checkVoiceUsers",
            "addVoiceUserLoop",
            "refillAiTokenLoop",
            "pingServerLoop",
            "backupDatabaseLoop",
            "removeExpiredClaimedBoosterRoles",
            "removeExpiredClaimedBoosterChannels",
            "sendScheduledMessages",
            "pollTwitchStreams",
            "clearNotifiedUsersLoop",
            "sendPokemonWerbung",
        ]:
            setattr(cog, attr, _running_task())
        bot.get_cog.return_value = cog
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.DEGRADED
        assert "invalid" in result.message

    @pytest.mark.asyncio
    async def test_degraded_when_is_running_raises_attribute_error(self, bot):
        cog = MagicMock()

        class BadTask:
            @property
            def is_running(self):
                raise AttributeError("broken")

        cog.sendSendReadyGiveaways = BadTask()
        for attr in [
            "endGiveawaysLoop",
            "checkVoiceUsers",
            "addVoiceUserLoop",
            "refillAiTokenLoop",
            "pingServerLoop",
            "backupDatabaseLoop",
            "removeExpiredClaimedBoosterRoles",
            "removeExpiredClaimedBoosterChannels",
            "sendScheduledMessages",
            "pollTwitchStreams",
            "clearNotifiedUsersLoop",
            "sendPokemonWerbung",
        ]:
            setattr(cog, attr, _running_task())
        bot.get_cog.return_value = cog
        result = await BackgroundLoopHealthCheck(bot).run()
        assert result.status == HealthStatus.DEGRADED
        assert "invalid" in result.message
