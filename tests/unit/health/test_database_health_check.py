"""Tests for DatabaseHealthCheck."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from health.checks.database import DatabaseHealthCheck

from health.checks import HealthStatus


def _make_pool(
    size: int = 5,
    maxsize: int = 10,
    freesize: int = 8,
    select_result: tuple = (1,),
    acquire_timeout: bool = False,
):
    pool = MagicMock()
    pool.size = size
    pool.maxsize = maxsize
    pool.freesize = freesize
    pool.release = MagicMock()

    conn = MagicMock()
    cursor = AsyncMock()
    cursor.execute = AsyncMock()
    cursor.fetchone = AsyncMock(return_value=select_result)
    conn.cursor = MagicMock(return_value=AsyncMock())
    conn.cursor.return_value.__aenter__.return_value = cursor
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)

    if acquire_timeout:
        pool.acquire = AsyncMock(side_effect=TimeoutError)
    else:
        pool.acquire = AsyncMock(return_value=conn)

    return pool, conn, cursor


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
        pool, _, cursor = _make_pool()
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool):
            result = await check.run()
        assert result.status == HealthStatus.HEALTHY
        cursor.execute.assert_awaited_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_high_utilization_degraded(self, check: DatabaseHealthCheck):
        pool, _, _ = _make_pool(size=10, maxsize=10, freesize=1)
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool):
            result = await check.run()
        assert result.status == HealthStatus.DEGRADED
        assert "utilization" in result.message.lower()

    @pytest.mark.asyncio
    async def test_acquire_timeout_critical(self, check: DatabaseHealthCheck):
        pool, _, _ = _make_pool(acquire_timeout=True)
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "Timed out" in result.message

    @pytest.mark.asyncio
    async def test_unexpected_select_result(self, check: DatabaseHealthCheck):
        pool, _, _ = _make_pool(select_result=(0,))
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL

    @pytest.mark.asyncio
    async def test_connection_exception(self, check: DatabaseHealthCheck):
        pool = MagicMock()
        pool.acquire = AsyncMock(side_effect=Exception("connection refused"))
        with patch.object(DatabaseHealthCheck, "_get_pool", return_value=pool):
            result = await check.run()
        assert result.status == HealthStatus.CRITICAL
        assert "connection refused" in result.message
