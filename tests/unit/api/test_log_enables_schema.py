"""Tests for log_enables table bootstrap and API resilience."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from api import (  # noqa: E402
    _ensure_log_enable_row,
    _ensure_log_enables_table,
    get_log_enable,
    get_table_definitions,
    set_log_enable,
)
from tests.helpers.factories import GUILD_ID

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_log_enables_ensured() -> None:
    import api

    api._log_enables_table_ensured = False
    yield
    api._log_enables_table_ensured = False


class TestLogEnablesTableDefinitions:
    def test_log_enables_in_table_definitions(self) -> None:
        tables = get_table_definitions()
        assert "log_enables" in tables
        assert "CREATE TABLE IF NOT EXISTS `log_enables`" in tables["log_enables"]


class TestEnsureLogEnablesTable:
    @pytest.mark.asyncio
    async def test_ensure_creates_table_once(self) -> None:
        action = AsyncMock()
        with patch("api.execute_action", new=action):
            await _ensure_log_enables_table()
            await _ensure_log_enables_table()
        create_calls = [c for c in action.await_args_list if "CREATE TABLE" in c.args[0] and "log_enables" in c.args[0]]
        assert len(create_calls) == 1

    @pytest.mark.asyncio
    async def test_get_log_enable_ensures_table_before_select(self) -> None:
        call_order: list[str] = []

        async def track_action(query: str, params=None, bot=None) -> int:
            if "CREATE TABLE" in query and "log_enables" in query:
                call_order.append("create")
            return 1

        async def track_query(query: str, params=None, bot=None) -> None:
            if "FROM log_enables" in query:
                call_order.append("select")
            return None

        with patch("api.execute_action", side_effect=track_action), patch("api.execute_query", side_effect=track_query):
            result = await get_log_enable(GUILD_ID)
        assert call_order.index("create") < call_order.index("select")
        assert result.guild_id == str(GUILD_ID)

    @pytest.mark.asyncio
    async def test_set_log_enable_ensures_table_and_row(self) -> None:
        action = AsyncMock(return_value=1)
        with patch("api.execute_action", new=action):
            await set_log_enable(GUILD_ID, memberJoin=False)
        sqls = [c.args[0] for c in action.await_args_list]
        assert any("CREATE TABLE" in sql and "log_enables" in sql for sql in sqls)
        assert any("INSERT INTO log_enables" in sql and "ON DUPLICATE KEY" in sql for sql in sqls)
        assert any("UPDATE log_enables" in sql for sql in sqls)

    @pytest.mark.asyncio
    async def test_ensure_log_enables_table_retries_after_failed_ddl(self) -> None:
        action = AsyncMock(side_effect=[None, 1])
        with patch("api.execute_action", new=action):
            await _ensure_log_enables_table()
            await _ensure_log_enables_table()
        create_calls = [c for c in action.await_args_list if "CREATE TABLE" in c.args[0]]
        assert len(create_calls) == 2

    @pytest.mark.asyncio
    async def test_ensure_log_enable_row_uses_upsert(self) -> None:
        action = AsyncMock(return_value=1)
        with patch("api.execute_action", new=action):
            await _ensure_log_enable_row(GUILD_ID)
        upsert_calls = [c for c in action.await_args_list if "ON DUPLICATE KEY" in c.args[0]]
        assert upsert_calls
