"""Tests for DatabaseHealthCheck."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from health.checks.database import DatabaseHealthCheck, _ping_database

from health.checks import HealthStatus


def _make_pool(
    size: int = 5,
    maxsize: int = 10,
    freesize: int = 8,
):
    pool = MagicMock()
    pool.size = size
    pool.maxsize = maxsize
    pool.freesize = freesize
    return pool


class TestDatabaseHealthCheck:
    @pytest.fixture
    def check(self) -> DatabaseHealthCheck:
        return DatabaseHealthCheck()

    def test_name_and_critical(self, check: DatabaseHealthCheck):
        assert check.name == "Database"
        assert check.critical is True

    @pytest.mark.asyncio
    async def test_pool_none_returns_critical(self, check: DatabaseHealthCheck):
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=None):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "None" in result.message

    @pytest.mark.asyncio
    async def test_healthy_pool(self, check: DatabaseHealthCheck):
        pool = _make_pool()
        with (
            patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool),
            patch("health.checks.database._ping_database", new=AsyncMock()),
        ):
            result = await check.run()
        assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_high_utilization_degraded(self, check: DatabaseHealthCheck):
        pool = _make_pool(size=10, maxsize=10, freesize=1)
        with (
            patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool),
            patch("health.checks.database._ping_database", new=AsyncMock()),
        ):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
        assert "utilization" in result.message.lower()

    @pytest.mark.asyncio
    async def test_connect_timeout_critical(self, check: DatabaseHealthCheck):
        pool = _make_pool()
        with (
            patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool),
            patch(
                "health.checks.database._ping_database",
                new=AsyncMock(side_effect=TimeoutError),
            ),
        ):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "Timed out connecting" in result.message

    @pytest.mark.asyncio
    async def test_connection_exception(self, check: DatabaseHealthCheck):
        pool = _make_pool()
        with (
            patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool),
            patch(
                "health.checks.database._ping_database",
                new=AsyncMock(side_effect=Exception("connection refused")),
            ),
        ):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "connection refused" in result.message


class TestPingDatabase:
    @pytest.mark.asyncio
    async def test_unexpected_select_result(self):
        mock_cursor = AsyncMock()
        mock_cursor.execute = AsyncMock()
        mock_cursor.fetchone = AsyncMock(return_value=(0,))
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
        mock_conn.close = MagicMock()

        with patch("asyncmy.connect", new=AsyncMock(return_value=mock_conn)):
            with pytest.raises(ValueError, match="unexpected result"):
                await _ping_database()
