"""Behavioral tests for api.py database functions with mocked connections.

Replaces the previous existence-only tests with proper behavioral tests
that verify SQL query generation, return types, error handling, and edge cases.
"""

from collections.abc import Iterator
from datetime import datetime
from typing import Any, TypeVar
from unittest.mock import AsyncMock, MagicMock

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

# --- Mock Discord and aiohttp before importing api ---
import sys  # noqa: E402

_discord_mock = MagicMock()
_discord_mock.Entitlement = MagicMock()
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()
# -------------------------------------------------------

from api import (  # noqa: E402
    add_channel_to_blacklist,
    add_level_role,
    add_role_boost,
    add_role_to_blacklist,
    add_user_boost,
    add_warning,
    bulk_update_user_xp,
    check_if_opted_out,
    check_pool_health,
    clear_channel_overwrites,
    delete_level_system_data,
    execute_action,
    execute_query,
    get_channel_boost,
    get_channel_overwrites,
    get_level_roles,
    get_level_system_status,
    get_levelup_channel,
    get_levelup_message,
    get_levelup_message_status,
    get_user_boost,
    get_user_roles_boosts,
    get_warn_config,
    get_warnings,
    get_xp_scaling,
    opt_in,
    opt_out,
    remove_level_role,
    remove_warning,
    safe_execute_query,
    save_channel_overwrites,
    set_bot,
    set_custom_formula,
    set_level_system_status,
    set_levelup_channel,
    set_levelup_message,
    set_levelup_message_status,
    set_warn_config,
    set_xp_scaling,
    transaction,
)

# ---------------------------------------------------------------------------
# Helper: build a properly nested mock chain for asyncmy's pool/conn/cursor
#
# The chain in _execute_with_retry is:
#   conn = await asyncio.wait_for(pool.acquire(), timeout=10)
#   async with conn, conn.cursor() as cursor:
#       await cursor.execute(query, params)
#       return await callback(cursor, conn)
#
# So pool.acquire() must be awaitable and return something that supports
# async with (__aenter__/__aexit__) that yields itself, and .cursor() must
# be awaitable and support async with, yielding a cursor that has .execute
# and .fetchall / .fetchone methods.
# -------------------------------------------------------------------------
# Helper: async iterator that yields from a list

T = TypeVar("T")


class AsyncIter:
    """Utility async iterator that yields items from a given list."""

    def __init__(self, items: list) -> None:
        self._items = list(reversed(items))

    def __aiter__(self) -> "AsyncIter":
        return self

    async def __anext__(self) -> object:
        if not self._items:
            raise StopAsyncIteration
        return self._items.pop()


def make_mock_pool() -> tuple[Any, Any, Any]:
    """Create a complete async mock pool that mimics asyncmy connection pool."""
    cursor = AsyncMock(name="cursor")
    cursor.fetchall = AsyncMock(return_value=[])
    cursor.fetchone = AsyncMock(return_value=None)
    cursor.rowcount = 0
    cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))

    conn = MagicMock(name="conn")
    conn.cursor = MagicMock(return_value=AsyncMock())
    conn.cursor.return_value.__aenter__.return_value = cursor
    conn.__aenter__.return_value = conn
    conn.__aexit__.return_value = None
    conn.commit = AsyncMock()
    conn.rollback = AsyncMock()

    pool = MagicMock(name="pool")
    # pool.acquire returns an async context manager; awaiting it returns conn
    pool.acquire = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aenter__.return_value = conn

    return pool, conn, cursor


def make_bot(pool: object = None) -> tuple[MagicMock, object]:
    """Create a mock bot and set it as the global _bot."""
    if pool is None:
        pool, _, _ = make_mock_pool()
    bot = MagicMock(name="bot")
    bot._pool = pool
    set_bot(bot)
    return bot, pool


@pytest.fixture
def pool_conn_cursor() -> tuple[Any, Any, Any]:
    """Fixture returning (pool, conn, cursor) tuple."""
    pool, conn, cursor = make_mock_pool()
    return pool, conn, cursor


@pytest.fixture(autouse=True)
def reset_globals() -> Iterator[None]:
    """Reset global state in api.py between tests."""
    set_bot(None)
    from api import _blacklist_cache, _guild_config_cache

    _guild_config_cache.clear()
    _blacklist_cache.clear()
    yield


@pytest.fixture
def bot_with_pool(pool_conn_cursor: tuple[Any, Any, Any]) -> tuple[Any, Any]:
    """Fixture that sets up a global bot and returns (bot, cursor)."""
    pool, conn, cursor = pool_conn_cursor
    bot = MagicMock(name="bot")
    bot._pool = pool
    set_bot(bot)
    return bot, cursor


# ---------------------------------------------------------------------------
# execute_query
# ---------------------------------------------------------------------------


class TestExecuteQuery:
    """Tests for execute_query - core query execution."""

    @pytest.mark.asyncio
    async def test_returns_fetchall_results(self, bot_with_pool: tuple[MagicMock, AsyncMock]):
        """Should return rows from cursor.fetchall()."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [("active", 1)]
        cursor.execute = AsyncMock()

        result = await execute_query("SELECT active FROM levelConfig WHERE guild_id = %s", ("123",))

        cursor.execute.assert_awaited_once()
        assert result == [("active", 1)]

    @pytest.mark.asyncio
    async def test_returns_none_when_no_pool(self):
        """Should return None when no database pool is available."""
        result = await execute_query("SELECT 1")
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_on_no_results(self, bot_with_pool):
        """Should return None when fetchall returns None."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await execute_query("SELECT active FROM levelConfig WHERE guild_id = %s", ("123",))
        assert result is None


# ---------------------------------------------------------------------------
# safe_execute_query
# ---------------------------------------------------------------------------


class TestSafeExecuteQuery:
    """Tests for safe_execute_query - always-lists wrapper."""

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_pool(self):
        """Should return an empty list (not None) when pool is missing."""
        result = await safe_execute_query("SELECT 1")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_query_returns_none(self, bot_with_pool):
        """Should return [] when execute_query returns None."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await safe_execute_query("SELECT 1")
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_results_when_rows_exist(self, bot_with_pool):
        """Should pass through actual result rows."""
        _, cursor = bot_with_pool
        expected = [("a", 1), ("b", 2)]
        cursor.fetchall.return_value = expected
        cursor.execute = AsyncMock()

        result = await safe_execute_query("SELECT * FROM t")
        assert result == expected


# ---------------------------------------------------------------------------
# execute_action
# ---------------------------------------------------------------------------


class TestExecuteAction:
    """Tests for execute_action - INSERT/UPDATE/DELETE."""

    @pytest.mark.asyncio
    async def test_commits_and_returns_rowcount(self, bot_with_pool):
        """Should commit and return the affected row count."""
        _, cursor = bot_with_pool
        cursor.rowcount = 3
        cursor.execute = AsyncMock()

        result = await execute_action("UPDATE level SET xp = 0 WHERE guild_id = %s", ("123",))

        cursor.execute.assert_awaited_once()
        assert result == 3


# ---------------------------------------------------------------------------
# check_pool_health
# ---------------------------------------------------------------------------


class TestCheckPoolHealth:
    """Tests for check_pool_health."""

    @pytest.mark.asyncio
    async def test_returns_true_on_successful_ping(self, bot_with_pool):
        """Should return True when SELECT 1 succeeds."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        result = await check_pool_health()
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_no_pool(self):
        """Should return False when pool is not available."""
        result = await check_pool_health()
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_on_exception(self, bot_with_pool):
        """Should return False when the query throws."""
        _, cursor = bot_with_pool
        cursor.execute.side_effect = Exception("DB connection lost")

        result = await check_pool_health()
        assert result is False


# ---------------------------------------------------------------------------
# Level system
# ---------------------------------------------------------------------------


class TestLevelSystemStatus:
    """Tests for get/set level system status."""

    @pytest.mark.asyncio
    async def test_set_level_system_status_executes_upsert(self, bot_with_pool):
        """set_level_system_status should execute an INSERT ... ON DUPLICATE KEY UPDATE."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_level_system_status("123", True)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelConfig" in sql
        assert "ON DUPLICATE KEY UPDATE" in sql

    @pytest.mark.asyncio
    async def test_get_level_system_status_returns_true_when_no_config(self, bot_with_pool):
        """Should return True (default) when no levelConfig row exists."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None  # No results
        cursor.execute = AsyncMock()

        result = await get_level_system_status("123")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_level_system_status_returns_db_value(self, bot_with_pool):
        """Should return the value from the database when present."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(0,)]  # active = 0 (int from MySQL)
        cursor.execute = AsyncMock()

        result = await get_level_system_status("123")
        assert result == 0


class TestLevelupMessageStatus:
    """Tests for level-up message status."""

    @pytest.mark.asyncio
    async def test_set_levelup_message_status(self, bot_with_pool):
        """Should execute upsert for level_up_messageActive."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_levelup_message_status("123", False)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelConfig" in sql
        assert "level_up_messageActive" in sql

    @pytest.mark.asyncio
    async def test_get_levelup_message_status_default_true(self, bot_with_pool):
        """Should default to True when no config row exists."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await get_levelup_message_status("123")
        assert result is True

    @pytest.mark.asyncio
    async def test_get_levelup_message_status_from_db(self, bot_with_pool):
        """Should return value from DB query."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [(0,)]
        cursor.execute = AsyncMock()

        result = await get_levelup_message_status("123")
        assert result == 0  # MySQL TINYINT returns as int


class TestLevelupMessage:
    """Tests for level-up message content."""

    @pytest.mark.asyncio
    async def test_set_levelup_message(self, bot_with_pool):
        """Should execute upsert for level_up_message."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_levelup_message("123", "GG {user}!")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "level_up_message" in sql

    @pytest.mark.asyncio
    async def test_get_levelup_message_no_row(self, bot_with_pool):
        """Should return None when no config row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await get_levelup_message("123")
        assert result is None


class TestLevelupChannel:
    """Tests for level-up channel."""

    @pytest.mark.asyncio
    async def test_set_levelup_channel(self, bot_with_pool):
        """Should execute upsert for level_up_channel_id."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_levelup_channel("123", "456")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelConfig" in sql
        assert "level_up_channel_id" in sql

    @pytest.mark.asyncio
    async def test_set_levelup_channel_clears_with_none(self, bot_with_pool):
        """Should allow setting channel to None."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_levelup_channel("123", None)

        cursor.execute.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_levelup_channel_no_row(self, bot_with_pool):
        """Should return None when no config row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await get_levelup_channel("123")
        assert result is None


class TestXpScaling:
    """Tests for XP scaling functions."""

    @pytest.mark.asyncio
    async def test_set_xp_scaling(self, bot_with_pool):
        """Should execute upsert for difficulty/scaling."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_xp_scaling("123", "medium")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelConfig" in sql
        assert "difficulty" in sql

    @pytest.mark.asyncio
    async def test_get_xp_scaling_default(self, bot_with_pool):
        """Should return 'normal' as default when no config row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        result = await get_xp_scaling("123")
        assert result == "medium"  # default in _get_cached_config

    @pytest.mark.asyncio
    async def test_get_xp_scaling_from_db(self, bot_with_pool, reset_globals):
        """Should return the stored scaling value."""
        _, cursor = bot_with_pool
        # _get_cached_config uses fetchone() for a full row
        cursor.fetchone = AsyncMock(return_value=("123", 1, "hard", None, None, None, None, None, None))
        cursor.execute = AsyncMock()

        result = await get_xp_scaling("123")
        assert result == "hard"


class TestCustomFormula:
    """Tests for custom formula functions."""

    @pytest.mark.asyncio
    async def test_set_custom_formula(self, bot_with_pool):
        """Should execute upsert for customFormula."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_custom_formula("123", "xp * 2")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelConfig" in sql
        assert "customFormula" in sql

    @pytest.mark.asyncio
    async def test_get_custom_formula_no_row(self, bot_with_pool):
        """Should return None when no formula set."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = None
        cursor.execute = AsyncMock()

        from api import get_custom_formula

        result = await get_custom_formula("123")
        assert result is None


# ---------------------------------------------------------------------------
# Level roles
# ---------------------------------------------------------------------------


class TestLevelRoles:
    """Tests for level role management."""

    @pytest.mark.asyncio
    async def test_add_level_role(self, bot_with_pool):
        """Should insert a level role."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await add_level_role("123", "456", 10)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO levelRole" in sql

    @pytest.mark.asyncio
    async def test_get_level_roles_empty(self, bot_with_pool):
        """Should return empty list when no roles configured."""
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        cursor.execute = AsyncMock()

        results = [row async for row in get_level_roles("123")]
        assert results == []

    @pytest.mark.asyncio
    async def test_remove_level_role(self, bot_with_pool):
        """Should delete a level role."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await remove_level_role("123", "456")

        cursor.execute.assert_awaited_once()
        assert "DELETE FROM levelRole" in cursor.execute.call_args[0][0]


# ---------------------------------------------------------------------------
# XP Boosts
# ---------------------------------------------------------------------------


class TestXpBoosts:
    """Tests for XP boost management."""

    @pytest.mark.asyncio
    async def test_add_role_boost(self, bot_with_pool):
        """Should insert a role XP boost."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await add_role_boost("123", "456", 1.5, True)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO roleXpBoost" in sql

    @pytest.mark.asyncio
    async def test_add_user_boost(self, bot_with_pool):
        """Should insert a user XP boost."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await add_user_boost("123", "789", 2.0, False)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO userXpBoost" in sql

    @pytest.mark.asyncio
    async def test_get_user_boost_no_boost(self, bot_with_pool):
        """Should return None when no boost exists."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        cursor.execute = AsyncMock()

        result = await get_user_boost("123", "789")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_channel_boost_no_boost(self, bot_with_pool):
        """Should return None when no channel boost."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        cursor.execute = AsyncMock()

        result = await get_channel_boost("123", "ch456")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_roles_boosts(self, bot_with_pool):
        """Should return boosts for specific role IDs."""
        _, cursor = bot_with_pool
        # execute_query_iter does async for row in cursor:
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([(1.5, True)]))
        cursor.execute = AsyncMock()

        result = await get_user_roles_boosts("123", ["456"])
        assert len(result) == 1
        assert result[0].boost == 1.5
        assert result[0].additive is True


# ---------------------------------------------------------------------------
# Warnings
# ---------------------------------------------------------------------------


class TestWarnings:
    """Tests for warning management."""

    @pytest.mark.asyncio
    async def test_add_warning(self, bot_with_pool):
        """Should insert a warning."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()
        exp_date = datetime(2026, 6, 1)

        await add_warning("123", "456", "Spam", exp_date, "admin1")

        assert cursor.execute.await_count >= 1
        sql = cursor.execute.call_args_list[0][0][0]
        assert "INSERT INTO warnings" in sql
        params = cursor.execute.call_args_list[0][0][1]
        assert params[2] == "Spam"

    @pytest.mark.asyncio
    async def test_get_warnings_no_results(self, bot_with_pool):
        """Should return no results when no warnings exist."""
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        cursor.execute = AsyncMock()

        result = [row async for row in get_warnings("123")]
        assert result == []

    @pytest.mark.asyncio
    async def test_get_warnings_with_results(self, bot_with_pool):
        """Should return WarningModel instances."""
        from datetime import datetime

        _, cursor = bot_with_pool
        now = datetime.now()
        cursor.__aiter__ = MagicMock(
            return_value=AsyncIter(
                [
                    (1, "123", "456", "Spam", now, None, "admin1", 0),
                ]
            )
        )
        cursor.execute = AsyncMock()

        results = [row async for row in get_warnings("123", "456")]
        assert len(results) == 1
        assert results[0].reason == "Spam"
        assert results[0].user_id == "456"

    @pytest.mark.asyncio
    async def test_remove_warning(self, bot_with_pool):
        """Should delete a warning by ID."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await remove_warning(42)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "DELETE FROM warnings" in sql
        assert "WHERE id" in sql


class TestWarnConfig:
    """Tests for warn config."""

    @pytest.mark.asyncio
    async def test_set_warn_config(self, bot_with_pool):
        """Should upsert warn_config."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await set_warn_config("123", 7, 3, 60, 5, 10)

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO warn_config" in sql
        assert "ON DUPLICATE KEY UPDATE" in sql

    @pytest.mark.asyncio
    async def test_get_warn_config_no_config(self, bot_with_pool):
        """Should return None when no warn_config row exists."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        cursor.execute = AsyncMock()

        result = await get_warn_config("123")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_warn_config_returns_model(self, bot_with_pool):
        """Should return a WarnConfigModel from DB row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [("123", 7, 3, 60, 5, 10)]
        cursor.execute = AsyncMock()

        result = await get_warn_config("123")
        assert result is not None
        assert result.expiration_days == 7
        assert result.timeout_threshold == 3
        assert result.timeout_duration == 60
        assert result.kick_threshold == 5
        assert result.ban_threshold == 10


# ---------------------------------------------------------------------------
# Opt-out
# ---------------------------------------------------------------------------


class TestOptOut:
    """Tests for message tracking opt-out/in."""

    @pytest.mark.asyncio
    async def test_opt_out(self, bot_with_pool):
        """Should insert an opt-out record."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await opt_out("456")

        cursor.execute.assert_awaited_once()
        assert "INSERT INTO message_tracking_opt_out" in cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_opt_in(self, bot_with_pool):
        """Should delete an opt-out record."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await opt_in("456")

        cursor.execute.assert_awaited_once()
        assert "DELETE FROM message_tracking_opt_out" in cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_check_if_opted_out_true(self, bot_with_pool):
        """Should return True when user has a row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = [("456",)]
        cursor.execute = AsyncMock()

        result = await check_if_opted_out("456")
        assert result is True

    @pytest.mark.asyncio
    async def test_check_if_opted_out_false(self, bot_with_pool):
        """Should return False when user has no row."""
        _, cursor = bot_with_pool
        cursor.fetchall.return_value = []
        cursor.execute = AsyncMock()

        result = await check_if_opted_out("456")
        assert result is False


# ---------------------------------------------------------------------------
# Channel overwrites
# ---------------------------------------------------------------------------


class TestChannelOverwrites:
    """Tests for channel overwrite persistence."""

    @pytest.mark.asyncio
    async def test_save_channel_overwrites(self, bot_with_pool):
        """Should insert a channel overwrite record."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await save_channel_overwrites("ch1", "role1", '{"view": true}')

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO channel_overwrites" in sql

    @pytest.mark.asyncio
    async def test_get_channel_overwrites_empty(self, bot_with_pool):
        """Should return empty list when no overwrites."""
        _, cursor = bot_with_pool
        cursor.__aiter__ = MagicMock(return_value=AsyncIter([]))
        cursor.execute = AsyncMock()

        results = [row async for row in get_channel_overwrites("ch1")]
        assert results == []

    @pytest.mark.asyncio
    async def test_clear_channel_overwrites(self, bot_with_pool):
        """Should delete overwrites for a channel."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await clear_channel_overwrites("ch1")

        cursor.execute.assert_awaited_once()
        assert "DELETE FROM channel_overwrites" in cursor.execute.call_args[0][0]


# ---------------------------------------------------------------------------
# Blacklist
# ---------------------------------------------------------------------------


class TestBlacklist:
    """Tests for channel/role blacklist."""

    @pytest.mark.asyncio
    async def test_add_channel_to_blacklist(self, bot_with_pool):
        """Should insert a channel blacklist entry."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await add_channel_to_blacklist("123", "ch456", "test reason")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO blacklistedChannel" in sql

    @pytest.mark.asyncio
    async def test_add_role_to_blacklist(self, bot_with_pool):
        """Should insert a role blacklist entry."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await add_role_to_blacklist("123", "r789")

        cursor.execute.assert_awaited_once()
        sql = cursor.execute.call_args[0][0]
        assert "INSERT INTO blacklisted_role" in sql


# ---------------------------------------------------------------------------
# Bulk operations
# ---------------------------------------------------------------------------


class TestBulkOperations:
    """Tests for bulk and multi-table operations."""

    @pytest.mark.asyncio
    async def test_bulk_update_user_xp(self, bot_with_pool):
        """Should execute multiple updates in a transaction."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()
        updates = [("user1", 10), ("user2", 20)]

        await bulk_update_user_xp("123", updates)

        # Multiple cursor.execute calls (one per update)
        assert cursor.execute.await_count == len(updates)

    @pytest.mark.asyncio
    async def test_delete_level_system_data(self, bot_with_pool):
        """Should delete from all level-related tables."""
        _, cursor = bot_with_pool
        cursor.execute = AsyncMock()

        await delete_level_system_data("123")

        # Should execute one DELETE per table
        expected_tables = [
            "level",
            "blacklistedUser",
            "blacklisted_role",
            "blacklistedChannel",
            "userXpBoost",
            "roleXpBoost",
            "channelXpBoost",
            "levelRole",
            "levelConfig",
        ]
        assert cursor.execute.await_count == len(expected_tables)
        # Verify all tables are included
        all_sql = " ".join(call[0][0] for call in cursor.execute.call_args_list)
        for table in expected_tables:
            assert table in all_sql

    @pytest.mark.asyncio
    async def test_bulk_update_user_xp_handles_error_gracefully(self, bot_with_pool):
        """Should not raise on DB errors during bulk update."""
        _, cursor = bot_with_pool
        cursor.execute.side_effect = Exception("DB error")
        cursor.__aenter__.return_value = cursor

        # Should not raise
        await bulk_update_user_xp("123", [("user1", 10)])


# ---------------------------------------------------------------------------
# transaction context manager
# ---------------------------------------------------------------------------


class TestTransaction:
    """Tests for the transaction async context manager."""

    @pytest.mark.asyncio
    async def test_transaction_success(self):
        """Should commit on successful exit."""
        pool, conn, _ = make_mock_pool()
        bot = MagicMock(_pool=pool)
        set_bot(bot)

        async with transaction() as result_conn:
            assert result_conn is conn

        conn.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_exception(self):
        """Should rollback when an exception occurs."""
        pool, conn, _ = make_mock_pool()
        bot = MagicMock(_pool=pool)
        set_bot(bot)

        with pytest.raises(ValueError, match="test"):
            async with transaction():
                raise ValueError("test error")

        conn.rollback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transaction_raises_when_no_pool(self):
        """Should raise RuntimeError when pool is not initialized."""
        with pytest.raises(RuntimeError, match="Database pool is not initialized"):
            async with transaction():
                pass
