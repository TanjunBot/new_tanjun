"""Tests for health/manager.py HealthCheckManager."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from health.checks import HealthCheck, HealthCheckResult, HealthStatus
from health.manager import HealthCheckManager


class _HealthyCheck(HealthCheck):
    def __init__(self, name: str = "Healthy", critical: bool = False):
        self._name = name
        self._critical = critical

    @property
    def name(self) -> str:
        return self._name

    @property
    def critical(self) -> bool:
        return self._critical

    async def run(self) -> HealthCheckResult:
        return HealthCheckResult(self.name, HealthStatus.HEALTHY, "ok")


class _CriticalFailCheck(HealthCheck):
    @property
    def name(self) -> str:
        return "CriticalFail"

    @property
    def critical(self) -> bool:
        return True

    async def run(self) -> HealthCheckResult:
        return HealthCheckResult(self.name, HealthStatus.CRITICAL, "failed")


class _ExceptionCheck(HealthCheck):
    @property
    def name(self) -> str:
        return "ExceptionCheck"

    @property
    def critical(self) -> bool:
        return False

    async def run(self) -> HealthCheckResult:
        raise RuntimeError("boom")


@pytest.fixture
def manager() -> HealthCheckManager:
    bot = MagicMock()
    return HealthCheckManager(bot)


class TestHealthCheckManagerRegister:
    def test_register_check(self, manager: HealthCheckManager):
        check = _HealthyCheck()
        manager.register(check)
        assert len(manager._checks) == 1

    def test_register_with_interval(self, manager: HealthCheckManager):
        check = _HealthyCheck()
        manager.register(check, interval=60)
        assert manager._check_intervals["Healthy"] == 60


class TestHealthCheckManagerRunAll:
    @pytest.mark.asyncio
    async def test_run_all_empty(self, manager: HealthCheckManager):
        results = await manager.run_all()
        assert results == []

    @pytest.mark.asyncio
    async def test_run_all_healthy(self, manager: HealthCheckManager):
        manager.register(_HealthyCheck())
        results = await manager.run_all()
        assert len(results) == 1
        assert results[0].status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_run_all_handles_exception(self, manager: HealthCheckManager):
        manager.register(_ExceptionCheck())
        results = await manager.run_all()
        assert results[0].status == HealthStatus.CRITICAL
        assert "exception" in results[0].message.lower()


class TestHealthCheckManagerStartup:
    @pytest.mark.asyncio
    async def test_startup_all_healthy(self, manager: HealthCheckManager):
        manager.register(_HealthyCheck(critical=True))
        ok, failures = await manager.run_startup_checks()
        assert ok is True
        assert failures == []

    @pytest.mark.asyncio
    async def test_startup_critical_failure(self, manager: HealthCheckManager):
        manager.register(_CriticalFailCheck())
        ok, failures = await manager.run_startup_checks()
        assert ok is False
        assert len(failures) == 1

    @pytest.mark.asyncio
    async def test_notify_critical_failures(self, manager: HealthCheckManager):
        manager.register(_CriticalFailCheck())
        await manager.run_startup_checks()
        with patch("health.manager.notify_health_failures", new_callable=AsyncMock) as mock_notify:
            await manager.notify_critical_failures()
            mock_notify.assert_awaited_once()


class TestHealthCheckManagerPeriodic:
    @pytest.mark.asyncio
    async def test_start_periodic_invalid_interval(self, manager: HealthCheckManager):
        with pytest.raises(ValueError, match="interval must be > 0"):
            await manager.start_periodic_checks(interval=0)

    @pytest.mark.asyncio
    async def test_stop_periodic_checks(self, manager: HealthCheckManager):
        manager._running = True
        manager._periodic_task = None
        manager.stop_periodic_checks()
        assert manager._running is False

    @pytest.mark.asyncio
    async def test_start_periodic_already_running(self, manager: HealthCheckManager):
        manager._running = True
        await manager.start_periodic_checks(interval=60)
        assert manager._periodic_task is None

    @pytest.mark.asyncio
    async def test_run_all_stores_last_results(self, manager: HealthCheckManager):
        manager.register(_HealthyCheck("Stored"))
        await manager.run_all()
        assert "Stored" in manager._last_results

    @pytest.mark.asyncio
    async def test_startup_non_critical_degraded_still_ok(self, manager: HealthCheckManager):
        class _DegradedCheck(HealthCheck):
            @property
            def name(self) -> str:
                return "Degraded"

            @property
            def critical(self) -> bool:
                return False

            async def run(self) -> HealthCheckResult:
                return HealthCheckResult(self.name, HealthStatus.DEGRADED, "slow")

        manager.register(_DegradedCheck())
        ok, failures = await manager.run_startup_checks()
        assert ok is True
        assert failures == []

    @pytest.mark.asyncio
    async def test_notify_critical_failures_noop_when_healthy(self, manager: HealthCheckManager):
        manager.register(_HealthyCheck())
        await manager.run_startup_checks()
        with patch("health.manager.notify_health_failures", new_callable=AsyncMock) as mock_notify:
            await manager.notify_critical_failures()
        mock_notify.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_start_periodic_runs_checks(self, manager: HealthCheckManager):
        manager.register(_HealthyCheck("Periodic"), interval=1)
        with (
            patch("health.manager.asyncio.sleep", new=AsyncMock()),
            patch("time.time", side_effect=[0, 100, 200, 300]),
            patch("health.manager.notify_health_failures", new_callable=AsyncMock),
        ):
            await manager.start_periodic_checks(interval=60)
            assert manager._running is True
            assert manager._periodic_task is not None
            manager.stop_periodic_checks()

    @pytest.mark.asyncio
    async def test_start_periodic_notifies_on_failures(self, manager: HealthCheckManager):
        class _FailCheck(HealthCheck):
            @property
            def name(self) -> str:
                return "FailPeriodic"

            @property
            def critical(self) -> bool:
                return False

            async def run(self) -> HealthCheckResult:
                return HealthCheckResult(self.name, HealthStatus.CRITICAL, "bad")

        manager.register(_FailCheck(), interval=1)
        sleep_calls = 0

        async def fake_sleep(_interval):
            nonlocal sleep_calls
            sleep_calls += 1
            if sleep_calls >= 2:
                manager._running = False

        with (
            patch("health.manager.asyncio.sleep", side_effect=fake_sleep),
            patch("time.time", side_effect=[0, 100, 200]),
            patch("health.manager.notify_health_failures", new_callable=AsyncMock) as notify,
        ):
            await manager.start_periodic_checks(interval=60)
            await manager._periodic_task
            notify.assert_awaited()

    @pytest.mark.asyncio
    async def test_stop_periodic_cancels_task(self, manager: HealthCheckManager):
        task = MagicMock()
        manager._running = True
        manager._periodic_task = task
        manager.stop_periodic_checks()
        assert manager._running is False
        assert manager._periodic_task is None
        task.cancel.assert_called_once()
