"""Unit tests for api._execute_with_retry."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import _execute_with_retry, set_bot  # noqa: E402
from tests.helpers.db import make_mock_pool  # noqa: E402

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_bot():
    set_bot(None)
    yield
    set_bot(None)


async def _run_retry(pool, cursor, *, is_write: bool = False, side_effect=None):
    if side_effect is not None:
        cursor.execute = AsyncMock(side_effect=side_effect)
    bot = MagicMock(_pool=pool)
    set_bot(bot)
    callback = AsyncMock(return_value="ok")
    result = await _execute_with_retry(
        "test_op",
        callback,
        "SELECT 1",
        None,
        is_write=is_write,
    )
    return result, callback


class TestExecuteWithRetry:
    @pytest.mark.asyncio
    async def test_deadlock_retry_on_second_attempt(self):
        pool, conn, cursor = make_mock_pool()
        pool.release = MagicMock()
        deadlock = Exception("Deadlock found when trying to get lock")
        cursor.execute = AsyncMock(side_effect=[deadlock, None])

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result, callback = await _run_retry(pool, cursor)

        assert result == "ok"
        assert cursor.execute.await_count == 2
        assert pool.acquire.await_count == 2
        callback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_pool_acquire_timeout(self):
        pool, conn, cursor = make_mock_pool()
        pool.acquire = AsyncMock(side_effect=TimeoutError("pool acquire timeout"))
        pool.release = MagicMock()
        bot = MagicMock(_pool=pool)
        set_bot(bot)
        callback = AsyncMock()

        with patch("asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(TimeoutError, match=r"Timeout on test_op attempt"):
                await _execute_with_retry("test_op", callback, "SELECT 1")

        assert pool.acquire.await_count == 3
        callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_broken_connection_retry(self):
        pool, conn, cursor = make_mock_pool()
        pool.release = MagicMock()
        conn.close = MagicMock()
        broken = Exception("MySQL connection lost")
        cursor.execute = AsyncMock(side_effect=[broken, None])

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result, callback = await _run_retry(pool, cursor)

        assert result == "ok"
        conn.close.assert_called_once()
        pool.release.assert_called()
        assert cursor.execute.await_count == 2

    @pytest.mark.asyncio
    async def test_record_db_query_error_flag(self):
        pool, conn, cursor = make_mock_pool()
        pool.release = MagicMock()
        cursor.execute = AsyncMock(side_effect=ValueError("syntax error"))
        bot = MagicMock(_pool=pool)
        set_bot(bot)
        callback = AsyncMock()

        with patch("extensions.prometheus_metrics.record_db_query") as mock_record:
            with pytest.raises(ValueError, match="syntax error"):
                await _execute_with_retry("test_op", callback, "SELECT 1")

        mock_record.assert_called_once()
        assert mock_record.call_args.kwargs.get("error") is True

    @pytest.mark.asyncio
    async def test_record_db_query_success(self):
        pool, conn, cursor = make_mock_pool()
        pool.release = MagicMock()
        bot = MagicMock(_pool=pool)
        set_bot(bot)
        callback = AsyncMock(return_value=42)

        with patch("extensions.prometheus_metrics.record_db_query") as mock_record:
            result = await _execute_with_retry("test_op", callback, "SELECT 1")

        assert result == 42
        mock_record.assert_called_once()
        assert mock_record.call_args.kwargs.get("error") is False
