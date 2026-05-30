import asyncio
import hashlib
import json
import logging
import time
import uuid
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from discord import Entitlement

from models import (
    AISituationModel,
    BlacklistEntryModel,
    BlockedReporterModel,
    ChannelOverwriteModel,
    ClaimedBoosterChannelModel,
    ClaimedBoosterRoleModel,
    DetailedWarningModel,
    DynamicSlowmodeMessageModel,
    DynamicSlowmodeModel,
    GiveawayBlacklistEntryModel,
    GiveawayChannelRequirementModel,
    GiveawayModel,
    LeaveChannelModel,
    LevelLeaderboardEntryModel,
    LevelRoleModel,
    LevelRolesGroupModel,
    LogEnableModel,
    ReportModel,
    ScheduledMessageModel,
    TicketMessageModel,
    TicketModel,
    TokenOverviewModel,
    TriggerMessageChannelModel,
    TriggerMessageModel,
    TwitchOnlineNotificationModel,
    UserLevelInfoModel,
    WarnConfigModel,
    WarningModel,
    WelcomeChannelModel,
    XpBoostModel,
)

# ── Log blacklist (delegated to LogBlacklistRepository) ─────────────────────────────
from repositories.log_blacklist_repository import LogBlacklistType, log_blacklist_repo
from utility import get_level_for_xp_async, get_xp_for_level_async
from utils.cache import TTLCache


async def add_log_blacklist(guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> None:
    await log_blacklist_repo.add(guild_id, entity_id, blacklist_type)


async def remove_log_blacklist(guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> None:
    await log_blacklist_repo.remove(guild_id, entity_id, blacklist_type)


async def get_log_blacklist(guild_id: str, blacklist_type: LogBlacklistType) -> list[str]:
    return await log_blacklist_repo.get_all(guild_id, blacklist_type)


async def is_log_entity_blacklisted(guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> str | None:
    return await log_blacklist_repo.is_entity_blacklisted(guild_id, entity_id, blacklist_type)


logger = logging.getLogger(__name__)


class DatabaseManager:
    """Central database connection manager.

    Owns the connection pool and provides lifecycle management.
    All database operations in api.py resolve their pool through
    this manager instead of relying on global ``_bot`` state.
    """

    def __init__(self, pool: Any | None = None) -> None:
        self._pool: Any | None = pool

    @property
    def is_ready(self) -> bool:
        """Check whether the pool has been initialized."""
        return self._pool is not None

    def set_pool(self, pool: Any) -> None:
        """Set or replace the connection pool."""
        self._pool = pool

    # ── High-level query methods ────────────────────────────────────────

    async def execute_query(
        self,
        query: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
    ) -> list[tuple[Any, ...]] | None:
        """Execute a SELECT query and return all result rows."""
        if not self.is_ready:
            return None

        async def _callback(cursor: Any, conn: Any) -> list[tuple[Any, ...]]:
            return await cursor.fetchall()

        return await _execute_with_retry("execute_query", _callback, query, params)

    async def execute_action(
        self,
        query: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
    ) -> int | None:
        """Execute a write query (INSERT/UPDATE/DELETE) and return rowcount."""
        if not self.is_ready:
            return None

        async def _callback(cursor: Any, conn: Any) -> int:
            return cursor.rowcount

        return await _execute_with_retry("execute_action", _callback, query, params, is_write=True)

    async def execute_batch(
        self,
        query: str,
        params_list: list[tuple],
    ) -> None:
        """Execute a batch INSERT using executemany for bulk operations."""
        if not self.is_ready:
            raise RuntimeError("Database pool is not initialized")

        async def _callback(cursor: Any, conn: Any) -> None:
            await cursor.executemany(query, params_list)
            return None

        await _execute_with_retry("execute_batch", _callback, query, is_write=True)

    async def execute_insert_and_get_id(
        self,
        query: str,
        params: Sequence[Any] | dict[str, Any] | None = None,
    ) -> int | None:
        """Execute an INSERT and return the last inserted row ID."""
        if not self.is_ready:
            return None

        async def _callback(cursor: Any, conn: Any) -> int | None:
            await conn.commit()
            return cursor.lastrowid

        return await _execute_with_retry("execute_insert_and_get_id", _callback, query, params, is_write=True)

    async def check_health(self) -> bool:
        """Check if the database pool is healthy by running SELECT 1."""
        if not self.is_ready:
            return False
        return await check_pool_health()

    async def create_tables(self) -> None:
        """Create all database tables."""
        if not self.is_ready:
            return
        await create_tables()


# Module-level singleton — all DB functions resolve pools through this instance.
db_manager = DatabaseManager()

# Backward-compatible aliases so existing code continues to work.
# New code should use ``from api import db_manager`` and access
# ``db_manager._pool`` / ``db_manager.is_ready`` directly.
_bot = None


def set_bot(bot) -> None:
    """Set the pool from a bot object (backward-compat).

    Extracts ``bot._pool`` and stores it in the global
    ``DatabaseManager`` singleton.  Also keeps the old
    ``_bot`` reference for code that checks ``_bot`` directly.
    """
    global _bot
    _bot = bot
    if bot is not None and hasattr(bot, "_pool") and bot._pool is not None:
        db_manager._pool = bot._pool
    elif bot is None:
        # Clear the manager's pool when clearing _bot so test resets work
        db_manager._pool = None


def _get_pool():
    """Return the shared connection pool.

    Delegates to ``db_manager._pool`` so that all functions
    automatically use the DatabaseManager singleton.
    Falls back to the old ``_bot._pool`` path for safety.
    """
    if db_manager.is_ready:
        return db_manager._pool
    if _bot is not None and hasattr(_bot, "_pool") and _bot._pool is not None:
        db_manager._pool = _bot._pool
        return db_manager._pool
    return None


# Max retries for transient DB failures
_MAX_DB_RETRIES = 3
# Pool acquire timeout in seconds
_POOL_ACQUIRE_TIMEOUT = 10
# Query execution timeout in seconds
_QUERY_TIMEOUT = 30


def _query_safe_id(query: str) -> str:
    """Return a deterministic opaque hash of a query for logging (no SQL/params leaked)."""
    return hashlib.sha256(query.encode()).hexdigest()[:12]


def _sanitize_for_log(query: str, params: Any = None) -> str:
    """Log a safe query identifier without exposing raw SQL or parameters."""
    return f"q={_query_safe_id(query)}"


async def _execute_with_retry(
    operation: str,
    callback,
    query: str,
    params: Any = None,
    bot=None,
    *,
    is_write: bool = False,
) -> Any:
    """Execute a DB operation with retry logic for transient failures.

    For write operations (is_write=True), only retries on deadlock/server-abort
    """
    pool = _get_pool()
    if pool is None:
        print(f"Tried to execute {operation} without pool. Pool is not yet initialized. {_sanitize_for_log(query)}")
        return None

    last_exception = None
    safe_id = _sanitize_for_log(query)
    for attempt in range(_MAX_DB_RETRIES):
        try:
            conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
            async with conn, conn.cursor() as cursor:
                await asyncio.wait_for(cursor.execute(query, params), timeout=_QUERY_TIMEOUT)
                return await callback(cursor, conn)
        except TimeoutError:
            msg = f"Timeout on {operation} attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}"
            print(msg)
            last_exception = TimeoutError(msg)
            if attempt < _MAX_DB_RETRIES - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            continue
        except Exception as e:
            err_str = str(e).lower()
            # Determine which errors are safe to retry
            retryable = "deadlock" in err_str or "duplicate" in err_str or "abort" in err_str
            if not is_write:
                # Reads can also retry on connection/timeout issues
                retryable = retryable or "connection" in err_str or "timeout" in err_str
            if attempt < _MAX_DB_RETRIES - 1 and retryable:
                print(f"Transient error on {operation} attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}")
                await asyncio.sleep(0.5 * (attempt + 1))
                last_exception = e
                continue
            # Non-retryable error or final attempt: raise instead of silently returning None
            print(f"Error during {operation}: {e} — {safe_id}")
            raise

    if last_exception:
        print(f"All retries exhausted for {operation}: {safe_id}")
        raise last_exception


# ── Cache System ──────────────────────────────────────────────────────────────
# Centralised TTL caches.  Each cache owns its TTL and (optionally) max size;
# LRU eviction happens automatically when ``maxsize`` is set.

_blacklist_cache: TTLCache[str, dict[str, list[BlacklistEntryModel]]] = TTLCache(ttl=30)
_guild_config_cache: TTLCache[str, dict[str, Any]] = TTLCache(ttl=300, maxsize=2000)
# In-memory cache for XP cooldowns: (guild_id, user_id) -> last_xp_gain_timestamp
# Eliminates DB queries entirely when user is on cooldown
_last_xp_gain_cache: dict[tuple[str, str], float] = {}
# In-memory cache for counting configs: channel_id -> (counting_config, challenge_config, modes_config)
# Reduces 3 DB queries per message to in-memory lookup
_counting_cache: TTLCache[str, tuple[dict | None, dict | None, dict | None]] = TTLCache(ttl=30)


def _invalidate_guild_cache(guild_id: str) -> None:
    _blacklist_cache.delete(guild_id)
    _guild_config_cache.delete(guild_id)


def invalidate_counting_cache(channel_id: str | int) -> None:
    """Remove the counting config cache entry for a specific channel."""
    _counting_cache.delete(str(channel_id))


async def preload_guild_configs(bot=None) -> None:
    """Fetch all guild-level configs at startup to warm the cache.

    Single bulk query replaces ~12+ individual queries per guild on first message.
    """
    query = """
    SELECT guild_id, active, difficulty, customFormula, level_up_messageActive,
           level_up_message, level_up_channel_id, textCooldown, voiceCooldown
    FROM levelConfig
    """
    pool = _get_pool()
    if pool is None:
        return
    _guild_config_cache.clear()
    try:
        conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
        async with conn, conn.cursor() as cursor:
            await asyncio.wait_for(cursor.execute(query), timeout=_QUERY_TIMEOUT)
            async for row in cursor:
                guild_id = str(row[0])
                _guild_config_cache.set(
                    guild_id,
                    {
                        "active": row[1],
                        "scaling": row[2],
                        "custom_formula": row[3],
                        "level_up_message_active": row[4],
                        "level_up_message": row[5],
                        "level_up_channel_id": row[6],
                        "text_cooldown": row[7],
                        "voice_cooldown": row[8],
                    },
                )
    except Exception as e:
        print(f"Error preloading guild configs: {e}")


async def _get_cached_blacklist(guild_id: str) -> dict[str, list[BlacklistEntryModel]]:
    """Get blacklist with TTL cache (30s), reducing per-message DB queries by ~97%."""
    cached = _blacklist_cache.get(guild_id)
    if cached is not None:
        return cached
    data = await get_blacklist(guild_id)
    _blacklist_cache.set(guild_id, data)
    return data


async def _get_cached_config(guild_id: str, key: str, default: Any = None) -> Any:
    """Get a cached level config value with TTL check. Falls back to DB on miss."""
    cache_entry = _guild_config_cache.get(guild_id)
    if cache_entry is not None:
        return cache_entry.get(key, default)
    # Cache miss — reload from DB
    query = """
    SELECT guild_id, active, difficulty, customFormula, level_up_messageActive,
           level_up_message, level_up_channel_id, textCooldown, voiceCooldown
    FROM levelConfig WHERE guild_id = %s
    """
    pool = _get_pool()
    if pool is None:
        return default
    try:
        conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
        async with conn, conn.cursor() as cursor:
            await asyncio.wait_for(cursor.execute(query, (guild_id,)), timeout=_QUERY_TIMEOUT)
            row = await cursor.fetchone()
            if row:
                data = {
                    "active": row[1],
                    "scaling": row[2],
                    "custom_formula": row[3],
                    "level_up_message_active": row[4],
                    "level_up_message": row[5],
                    "level_up_channel_id": row[6],
                    "text_cooldown": row[7],
                    "voice_cooldown": row[8],
                }
                _guild_config_cache.set(guild_id, data)
                return data.get(key, default)
            # Cache the miss (no levelConfig row for this guild)
            _guild_config_cache.set(guild_id, {})
    except Exception as e:
        print(f"Error caching guild config for {guild_id}: {e}")
    return default


async def execute_query(
    query: str, params: Sequence[Any] | dict[str, Any] | None = None, bot=None
) -> list[tuple[Any, ...]] | None:
    async def _callback(cursor, connection):
        result = await cursor.fetchall()
        return result

    return await _execute_with_retry("execute_query", _callback, query, params, bot)


async def execute_action(query: str, params: Sequence[Any] | dict[str, Any] | None = None, bot=None) -> int | None:
    async def _callback(cursor, connection):
        await connection.commit()
        return cursor.rowcount

    return await _execute_with_retry("execute_action", _callback, query, params, bot, is_write=True)


async def execute_batch(query: str, params_list: list[tuple], bot=None) -> None:
    """Execute a batch INSERT using executemany for bulk operations.

    Reduces database round-trips by sending all rows in one query.
    """
    pool = _get_pool()
    if pool is None:
        raise RuntimeError("Database pool is not initialized")

    last_exception = None
    safe_id = _query_safe_id(query)
    for attempt in range(_MAX_DB_RETRIES):
        try:
            conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
            async with conn:
                async with conn.cursor() as cursor:
                    await asyncio.wait_for(cursor.executemany(query, params_list), timeout=_QUERY_TIMEOUT)
                await conn.commit()
            return
        except TimeoutError:
            msg = f"Timeout on execute_batch attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}"
            print(msg)
            last_exception = TimeoutError(msg)
            if attempt < _MAX_DB_RETRIES - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            continue
        except Exception as e:
            err_str = str(e).lower()
            # Determine which errors are safe to retry (mirroring _execute_with_retry for write operations)
            retryable = "deadlock" in err_str or "duplicate" in err_str or "abort" in err_str
            if attempt < _MAX_DB_RETRIES - 1 and retryable:
                print(f"Transient error on execute_batch attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}")
                await asyncio.sleep(0.5 * (attempt + 1))
                last_exception = e
                continue
            # Non-retryable error or final attempt: raise instead of silently failing
            print(f"Error during execute_batch: {e} — {safe_id}")
            raise

    if last_exception:
        print(f"All retries exhausted for execute_batch: {safe_id}")
        raise last_exception


async def execute_insert_and_get_id(query: str, params: Sequence[Any] | dict[str, Any] | None = None, bot=None) -> int | None:
    async def _callback(cursor, connection):
        await connection.commit()
        await cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = await cursor.fetchone()
        return last_id[0] if last_id else None

    return await _execute_with_retry("execute_insert_and_get_id", _callback, query, params, bot, is_write=True)


async def execute_query_iter(
    query: str, params: Sequence[Any] | dict[str, Any] | None = None, bot=None
) -> AsyncIterator[tuple[Any, ...]]:
    """Async generator that yields rows one at a time for large result sets."""
    pool = _get_pool()
    if pool is None:
        print(f"Tried to execute_query_iter without pool. {_sanitize_for_log(query)}")
        return

    safe_id = _query_safe_id(query)
    yielded_any = False
    for attempt in range(_MAX_DB_RETRIES):
        try:
            conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
            async with conn, conn.cursor() as cursor:
                await asyncio.wait_for(cursor.execute(query, params), timeout=_QUERY_TIMEOUT)
                async for row in cursor:
                    yielded_any = True
                    yield row
            return
        except TimeoutError:
            if yielded_any:
                logger.error(f"Timeout after yielding rows on execute_query_iter: {safe_id}")
                raise
            print(f"Timeout on execute_query_iter attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}")
            if attempt < _MAX_DB_RETRIES - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            continue
        except Exception as e:
            if yielded_any:
                logger.error(f"Error after yielding rows during query iteration: {e} — {safe_id}")
                raise
            err_str = str(e).lower()
            retryable = "deadlock" in err_str or "connection" in err_str or "timeout" in err_str
            if attempt < _MAX_DB_RETRIES - 1 and retryable:
                print(f"Transient error on execute_query_iter attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}")
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            print(f"Error during query iteration: {e} — {safe_id}")
            return
    print(f"All retries exhausted for execute_query_iter: {safe_id}")


async def safe_execute_query(
    query: str, params: Sequence[Any] | dict[str, Any] | None = None, bot=None
) -> list[tuple[Any, ...]]:
    """Like execute_query but always returns a list (empty on error)."""
    result = await execute_query(query, params, bot)
    return result if result is not None else []


@asynccontextmanager
async def transaction(bot=None):
    """Async context manager for DB transactions with automatic rollback on error."""
    pool = _get_pool()
    if pool is None:
        raise RuntimeError("Database pool is not initialized")

    for attempt in range(_MAX_DB_RETRIES):
        safe_id = str(uuid.uuid4())
        try:
            conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
            async with conn:
                try:
                    yield conn
                    await conn.commit()
                except Exception:
                    await conn.rollback()
                    raise
            return
        except TimeoutError:
            print(f"Timeout on transaction acquire attempt {attempt + 1}/{_MAX_DB_RETRIES}: {safe_id}")
            if attempt < _MAX_DB_RETRIES - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
            continue
        except Exception:
            raise
    raise RuntimeError(f"Could not acquire database connection after {_MAX_DB_RETRIES} attempts [{safe_id}]")


async def check_pool_health(bot=None) -> bool:
    """Check if the database pool is healthy by running SELECT 1."""
    pool = _get_pool()
    if pool is None:
        return False
    for attempt in range(_MAX_DB_RETRIES):
        try:
            conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
            async with conn, conn.cursor() as cursor:
                await asyncio.wait_for(cursor.execute("SELECT 1"), timeout=_QUERY_TIMEOUT)
            return True
        except Exception:
            if attempt < _MAX_DB_RETRIES - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            return False
    return False


async def bulk_update_user_xp(
    guild_id: str,
    updates: list[tuple[str, int]],
    bot=None,
) -> None:
    """Update XP for multiple users in a single transaction."""
    try:
        async with transaction(bot) as conn, conn.cursor() as cursor:
            for user_id, xp_to_add in updates:
                await cursor.execute(
                    "INSERT INTO level (user_id, guild_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s",
                    (user_id, guild_id, xp_to_add, xp_to_add),
                )
    except Exception as e:
        safe_id = _query_safe_id("bulk_update_user_xp")
        print(f"Error during bulk XP update: {e} — {safe_id}")


def get_table_defs() -> dict[str, "TableDef"]:
    """Return table definitions as Pydantic TableDef models.

    Use this for introspection, testing, and programmatic schema access.
    Converted incrementally from get_table_definitions().
    """
    from table_def_models.table_def import TableDef, col, idx

    _t: dict[str, TableDef] = {}

    # ── Simple tables (mostly 1-3 columns, no FKs) ────────────────────────
    _t["channel_overwrites"] = TableDef(
        name="channel_overwrites",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("channel_id", "VARCHAR(20)", nullable=False),
            col("role_id", "VARCHAR(20)", nullable=False),
            col("overwrites", "JSON"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["message_tracking_opt_out"] = TableDef(
        name="message_tracking_opt_out",
        columns=[col("user_id", "VARCHAR(20)", pk=True)],
    )
    _t["counting"] = TableDef(
        name="counting",
        columns=[
            col("channel_id", "VARCHAR(20)", pk=True),
            col("progress", "INT UNSIGNED", default="0"),
            col("last_counter_id", "VARCHAR(20)", default="NULL"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _t["counting_challenge"] = TableDef(
        name="counting_challenge",
        columns=[
            col("channel_id", "VARCHAR(20)", pk=True),
            col("progress", "INT UNSIGNED", default="0"),
            col("last_counter_id", "VARCHAR(20)", default="NULL"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _t["counting_modes"] = TableDef(
        name="counting_modes",
        columns=[
            col("channel_id", "VARCHAR(20)", pk=True),
            col("progress", "INT", default="0"),
            col("mode", "TINYINT UNSIGNED", default="0"),
            col("goal", "INT"),
            col("last_counter_id", "VARCHAR(20)", default="NULL"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _t["wordchain"] = TableDef(
        name="wordchain",
        columns=[
            col("channel_id", "VARCHAR(20)", pk=True),
            col("word", "VARCHAR(1028)", default="NULL"),
            col("last_user_id", "VARCHAR(20)", default="NULL"),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _t["blacklistedUser"] = TableDef(
        name="blacklistedUser",
        primary_key=["user_id", "guild_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("reason", "VARCHAR(255)", default="NULL"),
            col("blacklisted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["blacklisted_role"] = TableDef(
        name="blacklisted_role",
        primary_key=["role_id", "guild_id"],
        columns=[
            col("role_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("reason", "VARCHAR(255)", default="NULL"),
            col("blacklisted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["blacklistedChannel"] = TableDef(
        name="blacklistedChannel",
        primary_key=["channel_id", "guild_id"],
        columns=[
            col("channel_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("reason", "VARCHAR(255)", default="NULL"),
            col("blacklisted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["userXpBoost"] = TableDef(
        name="userXpBoost",
        primary_key=["user_id", "guild_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("boost", "DECIMAL(4, 2) UNSIGNED", default="1"),
            col("additive", "TINYINT(1)", default="0"),
            col("boosted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["roleXpBoost"] = TableDef(
        name="roleXpBoost",
        primary_key=["role_id", "guild_id"],
        columns=[
            col("role_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("boost", "DECIMAL(4, 2) UNSIGNED", default="1"),
            col("additive", "TINYINT(1)", default="0"),
            col("boosted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["channelXpBoost"] = TableDef(
        name="channelXpBoost",
        primary_key=["channel_id", "guild_id"],
        columns=[
            col("channel_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("boost", "DECIMAL(4, 2) UNSIGNED", default="1"),
            col("additive", "TINYINT(1)", default="0"),
            col("boosted_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
        ],
    )
    _t["levelRole"] = TableDef(
        name="levelRole",
        primary_key=["role_id", "guild_id"],
        columns=[
            col("role_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("level", "INT UNSIGNED", default="0"),
        ],
    )
    _t["autopublish"] = TableDef(
        name="autopublish",
        columns=[col("channel_id", "VARCHAR(20)", pk=True)],
    )
    _t["feedbackBlocked"] = TableDef(
        name="feedbackBlocked",
        columns=[col("user_id", "VARCHAR(20)", pk=True)],
    )
    _t["afk_users"] = TableDef(
        name="afk_users",
        columns=[
            col("user_id", "VARCHAR(20)", pk=True),
            col("reason", "VARCHAR(1024)"),
        ],
    )
    _t["mediaChannel"] = TableDef(
        name="mediaChannel",
        columns=[
            col("channel_id", "VARCHAR(20)", pk=True),
            col("guild_id", "VARCHAR(20)"),
        ],
    )
    _t["brawlstarsLinkedAccounts"] = TableDef(
        name="brawlstarsLinkedAccounts",
        columns=[
            col("user_id", "VARCHAR(20)", pk=True),
            col("brawlstarsTag", "VARCHAR(20)"),
        ],
    )

    # ── Medium tables (5-10 columns, PK, indices) ─────────────────────────
    _t["warnings"] = TableDef(
        name="warnings",
        columns=[
            col("id", "INT", pk=True, ai=True),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("user_id", "VARCHAR(20)", nullable=False),
            col("reason", "VARCHAR(255)"),
            col("created_at", "TIMESTAMP", default="CURRENT_TIMESTAMP"),
            col("expires_at", "TIMESTAMP", default="NULL"),
            col("created_by", "VARCHAR(20)", nullable=False),
            col("escalation_level", "INT", default="0"),
        ],
        indices=[idx("idx_warnings_user_guild", "user_id", "guild_id")],
    )
    _t["warn_config"] = TableDef(
        name="warn_config",
        columns=[
            col("guild_id", "VARCHAR(20)", pk=True),
            col("expiration_days", "INT", default="0"),
            col("timeout_threshold", "INT", default="0"),
            col("timeout_duration", "INT", default="0"),
            col("kick_threshold", "INT", default="0"),
            col("ban_threshold", "INT", default="0"),
        ],
    )
    _t["level"] = TableDef(
        name="level",
        primary_key=["user_id", "guild_id"],
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("xp", "INT UNSIGNED", default="0"),
            col("customBackground", "VARCHAR(255)", default="NULL"),
            col("last_xp_gain", "DATETIME", default="NOW()"),
            col("last_voice_xp_gain", "DATETIME", default="NOW()"),
        ],
        indices=[idx("idx_level_guild_xp", "guild_id", "xp DESC")],
    )
    _t["levelConfig"] = TableDef(
        name="levelConfig",
        engine="InnoDB",
        charset="utf8mb4",
        columns=[
            col("guild_id", "VARCHAR(20)", pk=True),
            col("difficulty", "ENUM('easy', 'medium', 'hard', 'extreme', 'custom')", default="'medium'"),
            col("customFormula", "VARCHAR(255)", default="NULL"),
            col("level_up_messageActive", "TINYINT(1)", default="1"),
            col("level_up_message", "VARCHAR(1000)", default="NULL"),
            col("level_up_channel_id", "VARCHAR(20)", default="NULL"),
            col("active", "TINYINT(1)", default="1"),
            col("textCooldown", "INT", default="60"),
            col("voiceCooldown", "INT", default="60"),
        ],
    )
    _t["aiToken"] = TableDef(
        name="aiToken",
        columns=[
            col("freeToken", "SMALLINT UNSIGNED", default="500"),
            col("plusToken", "SMALLINT UNSIGNED", default="0"),
            col("paidToken", "INT UNSIGNED", default="0"),
            col("usedToken", "INT UNSIGNED", default="0"),
            col("user_id", "VARCHAR(20)", pk=True),
        ],
    )
    _t["afkMessages"] = TableDef(
        name="afkMessages",
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("messageId", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)"),
        ],
        primary_key=["user_id", "messageId"],
    )
    _t["giveawayParticipant"] = TableDef(
        name="giveawayParticipant",
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("giveaway_id", "INT UNSIGNED", nullable=False),
        ],
        primary_key=["user_id", "giveaway_id"],
    )
    _t["giveawayRoleRequirement"] = TableDef(
        name="giveawayRoleRequirement",
        columns=[
            col("role_id", "VARCHAR(20)", nullable=False),
            col("giveaway_id", "INT UNSIGNED", nullable=False),
        ],
        primary_key=["role_id", "giveaway_id"],
    )
    _t["giveawayBlacklistedRole"] = TableDef(
        name="giveawayBlacklistedRole",
        columns=[
            col("role_id", "VARCHAR(20)", pk=True),
            col("guild_id", "VARCHAR(20)"),
            col("reason", "VARCHAR(255)", default="NULL"),
        ],
    )
    _t["giveawayBlacklistedUser"] = TableDef(
        name="giveawayBlacklistedUser",
        columns=[
            col("user_id", "VARCHAR(20)", nullable=False),
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("reason", "VARCHAR(255)", default="NULL"),
        ],
        primary_key=["user_id", "guild_id"],
    )
    _t["blockedReporters"] = TableDef(
        name="blockedReporters",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("user_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "user_id"],
    )
    _t["reportchannel"] = TableDef(
        name="reportchannel",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )
    _t["booster_channel"] = TableDef(
        name="booster_channel",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )
    _t["boosterRole"] = TableDef(
        name="boosterRole",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("role_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "role_id"],
    )
    _t["log_channel"] = TableDef(
        name="log_channel",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )
    _t["log_channel_blacklist"] = TableDef(
        name="log_channel_blacklist",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )
    _t["logRoleBlacklist"] = TableDef(
        name="logRoleBlacklist",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("role_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "role_id"],
    )
    _t["logBlacklistChannel"] = TableDef(
        name="logBlacklistChannel",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )
    _t["logUserBlacklist"] = TableDef(
        name="logUserBlacklist",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("user_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "user_id"],
    )
    _t["join_to_create_channel"] = TableDef(
        name="join_to_create_channel",
        columns=[
            col("guild_id", "VARCHAR(20)", nullable=False),
            col("channel_id", "VARCHAR(20)", nullable=False),
        ],
        primary_key=["guild_id", "channel_id"],
    )

    return _t


def get_table_definitions() -> dict[str, str]:
    """Return the table DDL definitions used by create_tables.

    Exported for testing purposes to avoid DDL duplication.
    Now uses Pydantic TableDef models for a growing subset of tables;
    remaining tables still use raw SQL strings.
    """
    tables: dict[str, str] = {}

    # Convert model-backed tables
    for name, tdef in get_table_defs().items():
        tables[name] = tdef.to_sql()

    # ── Tables still using raw SQL (not yet converted to models) ────────
    tables["giveaway"] = """
    CREATE TABLE IF NOT EXISTS `giveaway` (
        `giveaway_id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
        `guild_id` VARCHAR(20) NOT NULL,
        `title` VARCHAR(128) NOT NULL,
        `description` VARCHAR(1024),
        `winners` TINYINT(4) DEFAULT 1,
        `withButton` TINYINT(1) DEFAULT 1,
        `customName` VARCHAR(32),
        `sponsor` VARCHAR(20),
        `price` VARCHAR(64),
        `message` VARCHAR(128),
        `endtime` DATETIME NOT NULL,
        `starttime` DATETIME,
        `started` TINYINT(1) DEFAULT 0,
        `ended` TINYINT(1) DEFAULT 0,
        `newMessageRequirement` SMALLINT UNSIGNED,
        `dayRequirement` SMALLINT UNSIGNED,
        `voiceRequirement` SMALLINT UNSIGNED,
        `sendFailed` TINYINT(1) DEFAULT 0,
        `channel_id` VARCHAR(20),
        `messageId` VARCHAR(20) DEFAULT "pending",
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX `idx_giveaway_ended_endtime` (`ended`, `endtime`)
    ) ENGINE=InnoDB;
    """
    tables["giveaway_channelRequirement"] = """
    CREATE TABLE IF NOT EXISTS `giveaway_channelRequirement` (
        `giveaway_id` INT UNSIGNED,
        `channel_id` VARCHAR(20),
        `amount` SMALLINT UNSIGNED,
        PRIMARY KEY(`giveaway_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayVoiceTime"] = """
    CREATE TABLE IF NOT EXISTS `giveawayVoiceTime` (
        `giveaway_id` INT UNSIGNED,
        `user_id` VARCHAR(20),
        `voiceMinutes` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveaway_id`, `user_id`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayNewMessage"] = """
    CREATE TABLE IF NOT EXISTS `giveawayNewMessage` (
        `giveaway_id` INT UNSIGNED,
        `user_id` VARCHAR(20),
        `messages` MEDIUMINT UNSIGNED,
        PRIMARY KEY(`giveaway_id`, `user_id`)
    ) ENGINE=InnoDB;
    """
    tables["giveaway_channelMessages"] = """
    CREATE TABLE IF NOT EXISTS `giveaway_channelMessages` (
        `giveaway_id` INT UNSIGNED,
        `channel_id` VARCHAR(20),
        `user_id` VARCHAR(20),
        `amount` MEDIUMINT UNSIGNED DEFAULT 0,
        PRIMARY KEY(`giveaway_id`, `channel_id`, `user_id`)
    ) ENGINE=InnoDB;
    """
    tables["aiSituations"] = """
    CREATE TABLE IF NOT EXISTS `aiSituations` (
        `user_id` VARCHAR(20) PRIMARY KEY,
        `situation` VARCHAR(4000) DEFAULT NULL,
        `name` VARCHAR(15) DEFAULT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `temperature` DECIMAL(3, 2) DEFAULT 1,
        `top_p` DECIMAL(3, 2) DEFAULT 1,
        `frequency_penalty` DECIMAL(3, 2) DEFAULT 0,
        `presence_penalty` DECIMAL(3, 2) DEFAULT 0,
        `unlocked` TINYINT(1) DEFAULT 0
    ) ENGINE=InnoDB;
    """
    tables["claimedBoosterChannel"] = """
    CREATE TABLE IF NOT EXISTS `claimedBoosterChannel` (
        `user_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        PRIMARY KEY(`user_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["claimedBoosterRole"] = """
    CREATE TABLE IF NOT EXISTS `claimedBoosterRole` (
        `user_id` VARCHAR(20),
        `role_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        PRIMARY KEY(`user_id`, `role_id`)
    ) ENGINE=InnoDB;
    """
    tables["log_enables"] = """
    CREATE TABLE IF NOT EXISTS `log_enables` (
        `guild_id` VARCHAR(20),
        `automodRuleCreate` TINYINT(1) DEFAULT 1,
        `automodRuleUpdate` TINYINT(1) DEFAULT 1,
        `automodRuleDelete` TINYINT(1) DEFAULT 1,
        `automodAction` TINYINT(1) DEFAULT 0,
        `guild_channelDelete` TINYINT(1) DEFAULT 1,
        `guild_channelCreate` TINYINT(1) DEFAULT 1,
        `guild_channelUpdate` TINYINT(1) DEFAULT 1,
        `guildUpdate` TINYINT(1) DEFAULT 1,
        `inviteCreate` TINYINT(1) DEFAULT 1,
        `inviteDelete` TINYINT(1) DEFAULT 0,
        `memberJoin` TINYINT(1) DEFAULT 1,
        `memberLeave` TINYINT(1) DEFAULT 1,
        `memberUpdate` TINYINT(1) DEFAULT 1,
        `userUpdate` TINYINT(1) DEFAULT 1,
        `memberBan` TINYINT(1) DEFAULT 1,
        `memberUnban` TINYINT(1) DEFAULT 1,
        `presenceUpdate` TINYINT(1) DEFAULT 1,
        `messageEdit` TINYINT(1) DEFAULT 1,
        `messageDelete` TINYINT(1) DEFAULT 1,
        `reactionAdd` TINYINT(1) DEFAULT 0,
        `reactionRemove` TINYINT(1) DEFAULT 0,
        `guildRoleCreate` TINYINT(1) DEFAULT 1,
        `guildRoleDelete` TINYINT(1) DEFAULT 1,
        `guildRoleUpdate` TINYINT(1) DEFAULT 1,
        PRIMARY KEY(`guild_id`)
    ) ENGINE=InnoDB;
    """
    tables["scheduledMessages"] = """
    CREATE TABLE IF NOT EXISTS `scheduledMessages` (
        `messageId` BIGINT PRIMARY KEY AUTO_INCREMENT,
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        `user_id` VARCHAR(20) NOT NULL,
        `content` VARCHAR(1024) NOT NULL,
        `send_time` DATETIME NOT NULL,
        `repeatInterval` MEDIUMINT UNSIGNED,
        `repeatAmount` MEDIUMINT UNSIGNED,
        `attachments` TEXT,
        `discord_message_id` VARCHAR(20) DEFAULT NULL,
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX `idx_sendtime` (send_time),
        INDEX `idx_user` (user_id),
        INDEX `idx_guild` (guild_id),
        INDEX `idx_discord_message` (discord_message_id)
    ) ENGINE=InnoDB;
    """
    tables["reports"] = """
    CREATE TABLE IF NOT EXISTS `reports` (
        `id` INT AUTO_INCREMENT,
        `guild_id` VARCHAR(20),
        `user_id` VARCHAR(20),
        `reporterId` VARCHAR(20),
        `reason` VARCHAR(1024),
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `accepted` TINYINT(1) DEFAULT 0,
        `accepted_at` TIMESTAMP DEFAULT NULL,
        `acceptedBy` VARCHAR(20) DEFAULT NULL,
        `resolved` TINYINT(1) DEFAULT 0,
        `resolved_at` TIMESTAMP DEFAULT NULL,
        `resolvedBy` VARCHAR(20) DEFAULT NULL,
        PRIMARY KEY(`id`)
    ) ENGINE=InnoDB;
    """
    tables["triggerMessages"] = """
    CREATE TABLE IF NOT EXISTS `triggerMessages` (
        `id` INT AUTO_INCREMENT,
        `guild_id` VARCHAR(20),
        `trigger` VARCHAR(128),
        `response` VARCHAR(1024),
        `case_sensitive` TINYINT(1) DEFAULT 0,
        PRIMARY KEY(`id`),
        INDEX `idx_guild` (`guild_id`)
    ) ENGINE=InnoDB;
    """
    tables["triggerMessagesChannel"] = """
    CREATE TABLE IF NOT EXISTS `triggerMessagesChannel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        `triggerId` INT,
        PRIMARY KEY(`guild_id`, `channel_id`, `triggerId`),
        FOREIGN KEY (`guild_id`, `triggerId`)
            REFERENCES `triggerMessages`(`guild_id`, `id`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["ticketMessages"] = """
    CREATE TABLE IF NOT EXISTS `ticketMessages` (
        `id` INT AUTO_INCREMENT,
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        `introduction` VARCHAR(1024),
        `pingRole` VARCHAR(20),
        `name` VARCHAR(128),
        `description` VARCHAR(1024),
        `summaryChannelId` VARCHAR(20),
        PRIMARY KEY(`id`),
        INDEX `idx_guild` (`guild_id`)
    ) ENGINE=InnoDB;
    """
    tables["tickets"] = """
    CREATE TABLE IF NOT EXISTS `tickets` (
        `guild_id` VARCHAR(20),
        `openerId` VARCHAR(20),
        `openedAt` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        `closed` TINYINT(1) DEFAULT 0,
        `closedAt` TIMESTAMP DEFAULT NULL,
        `closedBy` VARCHAR(20) DEFAULT NULL,
        `channel_id` VARCHAR(20),
        `ticketMessageId` INT,
        PRIMARY KEY(`guild_id`, `channel_id`, `ticketMessageId`),
        FOREIGN KEY (`guild_id`, `ticketMessageId`)
            REFERENCES `ticketMessages`(`guild_id`, `id`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["welcome_channel"] = """
    CREATE TABLE IF NOT EXISTS `welcome_channel` (
        `channel_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        `message` VARCHAR(1024) DEFAULT NULL,
        `imageBackground` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`channel_id`, `guild_id`)
    ) ENGINE=InnoDB;
    """
    tables["leave_channel"] = """
    CREATE TABLE IF NOT EXISTS `leave_channel` (
        `channel_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        `message` VARCHAR(1024) DEFAULT NULL,
        `imageBackground` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`channel_id`, `guild_id`)
    ) ENGINE=InnoDB;
    """
    tables["dynamicslowmode"] = """
    CREATE TABLE IF NOT EXISTS `dynamicslowmode` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        `messages` INT,
        `per` INT,
        `resetafter` INT,
        `cashedSlowmode` INT,
        PRIMARY KEY(`channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["dynamicslowmode_messages"] = """
    CREATE TABLE IF NOT EXISTS `dynamicslowmode_messages` (
        `id` INT AUTO_INCREMENT,
        `channel_id` VARCHAR(20),
        `messageId` VARCHAR(20),
        `send_time` DATETIME,
        PRIMARY KEY(`id`),
        INDEX `idx_channel` (`channel_id`),
        INDEX `idx_message` (`messageId`),
        INDEX `idx_sendtime` (`send_time`),
        FOREIGN KEY (`channel_id`)
            REFERENCES `dynamicslowmode`(`channel_id`)
            ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    tables["twitchOnlineNotification"] = """
    CREATE TABLE IF NOT EXISTS `twitchOnlineNotification` (
        `id` INT AUTO_INCREMENT,
        `channel_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        `twitchUuid` VARCHAR(64),
        `twitchName` VARCHAR(128),
        `notification_message` VARCHAR(1024) DEFAULT NULL,
        PRIMARY KEY(`id`),
        INDEX `idx_channel` (`channel_id`),
        INDEX `idx_guild` (`guild_id`)
    ) ENGINE=InnoDB;
    """

    return tables


async def create_tables(bot=None) -> None:
    """Create all database tables using get_table_definitions()."""
    tables = get_table_definitions()

    pool = _get_pool()
    if pool is None:
        return
    try:
        conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
        async with conn, conn.cursor() as cursor:
            await asyncio.wait_for(cursor.execute("SHOW TABLES"), timeout=_QUERY_TIMEOUT)
            existing = {row[0] for row in await cursor.fetchall()}
    except Exception as e:
        print(f"Error discovering existing tables: {e}")
        return

    # Build dependency map: table -> list of tables it depends on (via FK REFERENCES)
    dependencies = {
        "triggerMessagesChannel": ["triggerMessages"],
        "tickets": ["ticketMessages"],
        "dynamicslowmode_messages": ["dynamicslowmode"],
    }

    # Filter to only tables that need to be created
    to_create = {name for name in tables if name not in existing}

    # Topologically sort tables into batches for dependency-safe parallel creation
    created = set()
    batches = []
    while to_create:
        # Find all tables whose dependencies are satisfied (or have no dependencies)
        batch = {
            name for name in to_create if all(dep in created or dep not in to_create for dep in dependencies.get(name, []))
        }
        if not batch:
            # Circular dependency or missing parent - shouldn't happen with current schema
            raise RuntimeError(f"Cannot resolve table dependencies for: {to_create}")
        batches.append(batch)
        to_create -= batch
        created.update(batch)

    # Create tables in batches, parallelizing within each batch
    for batch in batches:
        await asyncio.gather(*[execute_action(tables[table_name], bot=bot) for table_name in batch])

    # Run schema migrations for existing tables that need column additions
    migrations = [
        # Add attachments column to scheduledMessages for attachment support
        """ALTER TABLE `scheduledMessages`
         ADD COLUMN `attachments` TEXT DEFAULT NULL
         AFTER `repeatAmount`""",
        # Add discord_message_id column to scheduledMessages for exact-match deletion
        """ALTER TABLE `scheduledMessages`
         ADD COLUMN `discord_message_id` VARCHAR(20) DEFAULT NULL
         AFTER `attachments`,
         ADD INDEX `idx_discord_message` (`discord_message_id`)""",
        """ALTER TABLE `level`
         ADD INDEX `idx_level_guild_xp` (`guild_id`, `xp` DESC)""",
        """ALTER TABLE `warnings`
         ADD INDEX `idx_warnings_user_guild` (`user_id`, `guild_id`)""",
        """ALTER TABLE `giveaway`
         ADD INDEX `idx_giveaway_ended_endtime` (`ended`, `endtime`)""",
    ]
    for migration in migrations:
        try:
            await execute_action(migration, bot=bot)
        except Exception as exc:
            exc_str = str(exc).lower()
            # Only suppress "column already exists" / duplicate column errors
            if "column already exists" in exc_str or "duplicate column" in exc_str or "duplicate column name" in exc_str:
                logging.debug("Migration skipped (column already exists): %s", migration[:60])
            else:
                logging.exception("Unexpected migration error: %s", migration[:60])
                raise


# ── Warning functions (delegated to WarningRepository) ───────────────────────────
from repositories.warning_repository import warning_repo


async def add_warning(
    guild_id: str | int, user_id: str | int, reason: str, created_by: str | int, expiration_date: datetime | None = None
) -> int:
    return await warning_repo.add(guild_id, user_id, reason, created_by, expiration_date)


async def get_warnings(guild_id: str | int, user_id: str | int | None = None) -> AsyncIterator[WarningModel]:
    async for row in warning_repo.get_all(guild_id, user_id):
        yield row


async def get_detailed_warnings(guild_id: str | int, user_id: str | int) -> AsyncIterator[DetailedWarningModel]:
    async for row in warning_repo.get_detailed(guild_id, user_id):
        yield row


async def remove_warning(warning_id: int) -> None:
    await warning_repo.remove(warning_id)


async def set_warn_config(
    guild_id: str | int,
    expiration_days: int,
    timeout_threshold: int,
    timeout_duration: int,
    kick_threshold: int,
    ban_threshold: int,
) -> None:
    await warning_repo.set_config(
        guild_id, expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold
    )


async def get_warn_config(guild_id: str | int) -> WarnConfigModel | None:
    return await warning_repo.get_config(guild_id)


async def save_channel_overwrites(channel_id: str | int, role_id: str | int, overwrites: str) -> None:
    query = "INSERT INTO channel_overwrites (channel_id, role_id, overwrites) VALUES (%s, %s, %s)"
    params = (channel_id, role_id, json.dumps(overwrites))
    await execute_action(query, params)


async def get_channel_overwrites(channel_id: str | int) -> AsyncIterator[ChannelOverwriteModel]:
    """Stream channel permission overwrites for a specific channel.

    Yields rows one at a time.
    """
    query = "SELECT role_id, overwrites FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    async for row in ChannelOverwriteModel.iter_rows(query, params):
        yield row


async def clear_channel_overwrites(channel_id: str | int) -> None:
    query = "DELETE FROM channel_overwrites WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def check_if_opted_out(user_id: str | int) -> bool:
    query = "SELECT * FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result is not None and len(result) > 0


async def opt_out(user_id: str | int) -> None:
    query = "INSERT INTO message_tracking_opt_out (user_id) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


async def opt_in(user_id: str | int) -> None:
    query = "DELETE FROM message_tracking_opt_out WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)


async def get_counting_configs(channel_id: str | int) -> tuple[dict | None, dict | None, dict | None]:
    """Fetch all counting configs (normal, challenge, modes) for a channel.

    Uses an in-memory cache with a short TTL to avoid 3 DB queries per message.
    Cache is invalidated via invalidate_counting_cache() when configs are mutated.

    Returns (counting_config, challenge_config, modes_config) where each is a dict
    with keys like 'progress', 'last_counter_id', 'guild_id', or None if not configured.
    """
    key = str(channel_id)
    cached = _counting_cache.get(key)
    if cached is not None:
        return cached[0], cached[1], cached[2]

    counting_query = "SELECT progress, last_counter_id, guild_id FROM counting WHERE channel_id = %s"
    challenge_query = "SELECT progress, last_counter_id, guild_id FROM counting_challenge WHERE channel_id = %s"
    modes_query = "SELECT progress, mode, goal, last_counter_id, guild_id FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    counting_result, challenge_result, modes_result = await asyncio.gather(
        execute_query(counting_query, params),
        execute_query(challenge_query, params),
        execute_query(modes_query, params),
    )
    counting_config = (
        {"progress": counting_result[0][0], "last_counter_id": counting_result[0][1], "guild_id": counting_result[0][2]}
        if counting_result
        else None
    )
    challenge_config = (
        {"progress": challenge_result[0][0], "last_counter_id": challenge_result[0][1], "guild_id": challenge_result[0][2]}
        if challenge_result
        else None
    )
    modes_config = (
        {
            "progress": modes_result[0][0],
            "mode": modes_result[0][1],
            "goal": modes_result[0][2],
            "last_counter_id": modes_result[0][3],
            "guild_id": modes_result[0][4],
        }
        if modes_result
        else None
    )
    _counting_cache.set(key, (counting_config, challenge_config, modes_config))
    return counting_config, challenge_config, modes_config


async def get_wordchain_word(channel_id: str | int) -> str | None:
    query = "SELECT word FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_wordchain_word(channel_id: Any, word: Any, guild_id: Any, worder_id: Any) -> None:
    query = "INSERT INTO wordchain (channel_id, word, last_user_id, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE word = %s, last_user_id = %s"
    params = (channel_id, word, worder_id, guild_id, word, worder_id)
    await execute_action(query, params)


async def get_wordchain_last_user_id(channel_id: str | int) -> str | None:
    query = "SELECT last_user_id FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_wordchain(channel_id: Any) -> None:
    query = "DELETE FROM wordchain WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def set_level_system_status(guild_id: str, active: bool) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, active=active)


async def get_level_system_status(guild_id: str) -> bool:
    """Check if the level system is enabled for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.active


async def delete_level_system_data(guild_id: str) -> None:
    tables = [
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
    # Validated mapping to avoid SQL injection from f-strings
    table_delete_queries = {
        "level": "DELETE FROM level WHERE guild_id = %s",
        "blacklistedUser": "DELETE FROM blacklistedUser WHERE guild_id = %s",
        "blacklisted_role": "DELETE FROM blacklisted_role WHERE guild_id = %s",
        "blacklistedChannel": "DELETE FROM blacklistedChannel WHERE guild_id = %s",
        "userXpBoost": "DELETE FROM userXpBoost WHERE guild_id = %s",
        "roleXpBoost": "DELETE FROM roleXpBoost WHERE guild_id = %s",
        "channelXpBoost": "DELETE FROM channelXpBoost WHERE guild_id = %s",
        "levelRole": "DELETE FROM levelRole WHERE guild_id = %s",
        "levelConfig": "DELETE FROM levelConfig WHERE guild_id = %s",
    }
    try:
        async with transaction() as conn, conn.cursor() as cursor:
            for table in tables:
                await cursor.execute(table_delete_queries[table], (guild_id,))
    except Exception as e:
        print(f"Error deleting level system data for guild {guild_id}: {e}")
        raise
    _invalidate_guild_cache(guild_id)


async def set_levelup_message_status(guild_id: str, status: bool) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, level_up_message_active=status)


async def get_levelup_message_status(guild_id: str) -> bool:
    """Get the level-up message status for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.level_up_message_active


async def set_levelup_message(guild_id: str, message: str) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, level_up_message=message)


async def get_levelup_message(guild_id: str) -> str | None:
    """Get the level-up message for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.level_up_message


async def set_levelup_channel(guild_id: str, channel_id: str | None) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, level_up_channel_id=channel_id)


async def get_levelup_channel(guild_id: str) -> str | None:
    """Get the level-up channel for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.level_up_channel_id


async def set_xp_scaling(guild_id: str, scaling: str) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, difficulty=scaling)


async def get_xp_scaling(guild_id: str) -> str:
    """Get the XP scaling for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.difficulty


async def set_custom_formula(guild_id: str, formula: str) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, custom_formula=formula, difficulty="custom")


async def get_custom_formula(guild_id: str) -> str | None:
    """Get the custom XP formula for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.custom_formula


async def add_level_role(guild_id: str, role_id: str, level: int) -> None:
    """Assign a level role (delegates to LevelRoleRepository)."""
    from repositories.level_role_repository import level_role_repo

    await level_role_repo.assign(guild_id, role_id, level)


async def get_level_roles(guild_id: str) -> AsyncIterator[LevelRoleModel]:
    """Stream level roles for a guild (delegates to LevelRoleRepository)."""
    from repositories.level_role_repository import level_role_repo

    async for row in level_role_repo.get_all(guild_id):
        yield row


async def get_level_role(guild_id: str, role_id: str) -> int | None:
    """Get level for a role (delegates to LevelRoleRepository)."""
    from repositories.level_role_repository import level_role_repo

    return await level_role_repo.get_by_role(guild_id, role_id)


async def remove_level_role(guild_id: str, role_id: str, _level: int | None = None) -> None:
    """Remove a level role (delegates to LevelRoleRepository)."""
    from repositories.level_role_repository import level_role_repo

    await level_role_repo.unassign(guild_id, role_id)


async def get_all_level_roles(guild_id: str) -> list[LevelRolesGroupModel]:
    """Get level roles grouped by level (delegates to LevelRoleRepository)."""
    from repositories.level_role_repository import level_role_repo

    return await level_role_repo.get_grouped_by_level(guild_id)


# ── XP Boost (delegated to XpBoostRepository) ──────────────────────────────────
from repositories.xp_boost_repository import BoostTarget, XpBoostRepository

# --- Legacy wrapper functions (backward compatible) ---


async def add_role_boost(guild_id: str, role_id: str, boost: float, additive: bool) -> None:
    await XpBoostRepository.add_boost(guild_id, role_id, boost, additive, BoostTarget.ROLE)


async def add_channel_boost(guild_id: str, channel_id: str, boost: float, additive: bool) -> None:
    await XpBoostRepository.add_boost(guild_id, channel_id, boost, additive, BoostTarget.CHANNEL)


async def add_user_boost(guild_id: str, user_id: str, boost: float, additive: bool) -> None:
    await XpBoostRepository.add_boost(guild_id, user_id, boost, additive, BoostTarget.USER)


async def remove_role_boost(guild_id: str, role_id: str) -> None:
    await XpBoostRepository.remove_boost(guild_id, role_id, BoostTarget.ROLE)


async def remove_channel_boost(guild_id: str, channel_id: str) -> None:
    await XpBoostRepository.remove_boost(guild_id, channel_id, BoostTarget.CHANNEL)


async def remove_user_boost(guild_id: str, user_id: str) -> None:
    await XpBoostRepository.remove_boost(guild_id, user_id, BoostTarget.USER)


async def get_all_boosts(guild_id: str) -> dict[str, list[XpBoostModel]]:
    return await XpBoostRepository.get_all_boosts(guild_id)


async def get_user_boost(guild_id: str, user_id: str) -> XpBoostModel | None:
    return await XpBoostRepository.get_boost(guild_id, user_id, BoostTarget.USER)


async def get_user_roles_boosts(guild_id: str, role_ids: list[str]) -> list[XpBoostModel]:
    return await XpBoostRepository.get_boosts_for_target(guild_id, role_ids, BoostTarget.ROLE)


async def get_channel_boost(guild_id: str, channel_id: str) -> XpBoostModel | None:
    return await XpBoostRepository.get_boost(guild_id, channel_id, BoostTarget.CHANNEL)


async def get_role_boost(guild_id: str, role_id: str) -> XpBoostModel | None:
    """Get a specific role XP boost. Added for consistency with user/channel boost pattern."""
    return await XpBoostRepository.get_boost(guild_id, role_id, BoostTarget.ROLE)


async def add_channel_to_blacklist(guild_id: str, channel_id: str, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklistedChannel (guild_id, channel_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, channel_id, reason)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def remove_channel_from_blacklist(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM blacklistedChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def add_role_to_blacklist(guild_id: str, role_id: str, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklisted_role (guild_id, role_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, role_id, reason)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def remove_role_from_blacklist(guild_id: str, role_id: str) -> None:
    query = "DELETE FROM blacklisted_role WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def add_user_to_blacklist(guild_id: str, user_id: str, reason: str | None = None) -> None:
    query = """
    INSERT INTO blacklistedUser (guild_id, user_id, reason)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
    """
    params = (guild_id, user_id, reason)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def remove_user_from_blacklist(guild_id: str, user_id: str) -> None:
    query = "DELETE FROM blacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_blacklist(guild_id: str) -> dict[str, list[BlacklistEntryModel]]:
    channels_query = "SELECT channel_id, reason FROM blacklistedChannel WHERE guild_id = %s"
    roles_query = "SELECT role_id, reason FROM blacklisted_role WHERE guild_id = %s"
    users_query = "SELECT user_id, reason FROM blacklistedUser WHERE guild_id = %s"

    channels: list[BlacklistEntryModel] = []
    async for row in BlacklistEntryModel.iter_rows(channels_query, (guild_id,)):
        channels.append(row)

    roles: list[BlacklistEntryModel] = []
    async for row in BlacklistEntryModel.iter_rows(roles_query, (guild_id,)):
        roles.append(row)

    users: list[BlacklistEntryModel] = []
    async for row in BlacklistEntryModel.iter_rows(users_query, (guild_id,)):
        users.append(row)

    return {
        "channels": channels,
        "roles": roles,
        "users": users,
    }


async def get_user_level_info(guild_id: str, user_id: str) -> UserLevelInfoModel | None:
    query = """
    SELECT xp, customBackground FROM level
    WHERE guild_id = %s AND user_id = %s
    """
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    scaling = await get_xp_scaling(guild_id)
    custom_formula = await get_custom_formula(guild_id)
    if result:
        formula = custom_formula or ""

        xp, custom_background = result[0]
        level = await get_level_for_xp_async(xp, scaling, formula)
        xp_needed = await get_xp_for_level_async(level, scaling, formula)
        xp_for_last_level_needed = await get_xp_for_level_async(level - 1, scaling, formula)
        return UserLevelInfoModel(
            xp=xp - xp_for_last_level_needed,
            level=level,
            xp_needed=xp_needed,
            custom_background=custom_background,
        )
    return None


async def set_custom_background(guild_id: str, user_id: str, background_url: str) -> None:
    query = """
    INSERT INTO level (guild_id, user_id, customBackground)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE customBackground = VALUES(customBackground)
    """
    params = (guild_id, user_id, background_url)
    await execute_action(query, params)


async def get_user_xp(guild_id: str, user_id: str) -> int | None:
    query = "SELECT xp FROM level WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def update_user_xp(guild_id: str, user_id: str, xp: int, respect_cooldown: bool = False) -> None:
    if respect_cooldown:
        cache_key = (guild_id, user_id)
        now = time.time()
        last_gain = _last_xp_gain_cache.get(cache_key)
        # Fetch cooldown from cache (subquery eliminated)
        cooldown_seconds = await _get_cached_config(guild_id, "text_cooldown", 60)
        if cooldown_seconds < 1:
            cooldown_seconds = 1  # Minimum 1-second floor
        if last_gain and (now - last_gain) < cooldown_seconds:
            return  # Still on cooldown — skip DB entirely
        # Proceed with single atomic DB update
        query = "INSERT INTO level (guild_id, user_id, xp, last_xp_gain) VALUES (%s, %s, %s, NOW()) ON DUPLICATE KEY UPDATE xp = xp + %s, last_xp_gain = NOW()"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)
        _last_xp_gain_cache[cache_key] = now
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)


async def update_user_xp_from_voice(guild_id: str, user_id: str, xp: int, respect_cooldown: bool = False) -> None:
    if respect_cooldown:
        cache_key = (guild_id, user_id)
        now = time.time()
        last_gain = _last_xp_gain_cache.get(cache_key)
        # Fetch cooldown from cache (subquery eliminated)
        cooldown_seconds = await _get_cached_config(guild_id, "voice_cooldown", 60)
        if cooldown_seconds < 5:
            cooldown_seconds = 5  # Minimum 5-second floor for voice
        if last_gain and (now - last_gain) < cooldown_seconds:
            return  # Still on cooldown — skip DB entirely
        # Proceed with single atomic DB update
        query = "INSERT INTO level (guild_id, user_id, xp, last_voice_xp_gain) VALUES (%s, %s, %s, NOW()) ON DUPLICATE KEY UPDATE xp = xp + %s, last_voice_xp_gain = NOW()"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)
        _last_xp_gain_cache[cache_key] = now
    else:
        query = "INSERT INTO level (guild_id, user_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s"
        params = (guild_id, user_id, xp, xp)
        await execute_action(query, params)


async def add_giveaway(
    guild_id: str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    channel_id: str,
    custom_name: str | None,
    sponsor: str | None,
    price: str | None,
    message: str | None,
    endtime: datetime,
    starttime: datetime | None,
    new_message_requirement: int | None,
    day_requirement: int | None,
    channel_requirements: dict[str, int],
    role_requirement: list[str],
    voice_requirement: int | None,
) -> int | None:
    from services.giveaway_service import GiveawayCreateParams, giveaway_service

    params = GiveawayCreateParams(
        guild_id=guild_id,
        title=title,
        description=description,
        winners=winners,
        with_button=with_button,
        channel_id=channel_id,
        custom_name=custom_name,
        sponsor=sponsor,
        price=price,
        message=message,
        end_time=endtime,
        start_time=starttime,
        new_message_requirement=new_message_requirement,
        day_requirement=day_requirement,
        channel_requirements=channel_requirements,
        role_requirement=role_requirement,
        voice_requirement=voice_requirement,
    )
    return await giveaway_service.create(params)


async def set_giveaway_message_id(giveaway_id: int, message_id: int) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.set_message_id(giveaway_id, message_id)


async def get_giveaway(giveaway_id: int) -> GiveawayModel | None:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get(giveaway_id)


async def get_giveaway_channel_requirements(giveaway_id: int) -> list[GiveawayChannelRequirementModel]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_channel_requirements(giveaway_id)


async def get_giveaway_role_requirements(giveaway_id: int) -> list[str]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_role_requirements(giveaway_id)


async def set_giveaway_started(giveaway_id: int) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.set_started(giveaway_id)


async def set_giveaway_ended(giveaway_id: int) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.set_ended(giveaway_id)


async def delete_old_giveaways() -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.delete_old()


async def get_giveaway_participants(giveaway_id: int) -> list[str]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_participants(giveaway_id)


async def get_new_messages(giveaway_id: int, user_id: str) -> int | None:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_new_messages(giveaway_id, user_id)


async def get_new_messages_channel(giveaway_id: int, channel_id: str, user_id: str) -> int | None:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_new_messages_channel(giveaway_id, channel_id, user_id)


async def get_voice_time(giveaway_id: int, user_id: str) -> int | None:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_voice_time(giveaway_id, user_id)


async def get_blacklisted_roles(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_blacklisted_roles(guild_id)


async def check_if_user_blacklisted(guild_id: str, user_id: str) -> bool:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.is_user_blacklisted(guild_id, user_id)


async def check_if_giveaway_participant(giveaway_id: int, user_id: str) -> bool:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.is_participant(giveaway_id, user_id)


async def remove_giveaway_participant(giveaway_id: int, user_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.remove_participant(giveaway_id, user_id)


async def add_giveaway_participant(giveaway_id: int, user_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_participant(giveaway_id, user_id)


async def get_send_ready_giveaways() -> list[int]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_send_ready()


async def add_giveaway_voice_minutes_if_needed(user_id: Any, guild_id: Any) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_voice_minutes(user_id, guild_id)


async def add_giveaway_new_message_if_needed(user_id: Any, guild_id: Any) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_new_message(user_id, guild_id)


async def add_giveaway_new_message_channel_if_needed(user_id: Any, guild_id: Any, channel_id: Any) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_new_message_channel(user_id, guild_id, channel_id)


async def get_end_ready_giveaways() -> list[int]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_end_ready()


async def add_giveaway_blacklisted_user(guild_id: str, user_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_blacklisted_user(guild_id, user_id)


async def add_giveaway_blacklisted_role(guild_id: str, role_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.add_blacklisted_role(guild_id, role_id)


async def remove_giveaway_blacklisted_user(guild_id: str, user_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.remove_blacklisted_user(guild_id, user_id)


async def remove_giveaway_blacklisted_role(guild_id: str, role_id: str) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.remove_blacklisted_role(guild_id, role_id)


async def get_giveaway_blacklisted_users(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_blacklisted_users(guild_id)


async def get_giveaway_blacklisted_roles(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    from services.giveaway_service import giveaway_service

    return await giveaway_service.get_blacklisted_roles(guild_id)


async def delete_giveaway(giveaway_id: int) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.delete(giveaway_id)


async def set_giveaway_endtime(giveaway_id: int, endtime: datetime) -> None:
    from services.giveaway_service import giveaway_service

    await giveaway_service.set_endtime(giveaway_id, endtime)


async def update_giveaway(
    giveaway_id: int,
    guild_id: str,
    title: str,
    description: str,
    winners: int,
    with_button: bool,
    custom_name: str | None,
    sponsor: str | None,
    price: str | None,
    message: str | None,
    endtime: datetime,
    starttime: datetime | None,
    new_message_requirement: int | None,
    day_requirement: int | None,
    channel_requirements: dict[str, int],
    role_requirement: list[str],
    voice_requirement: int | None,
    channel_id: str,
) -> None:
    from services.giveaway_service import GiveawayUpdateParams, giveaway_service

    params = GiveawayUpdateParams(
        guild_id=guild_id,
        title=title,
        description=description,
        winners=winners,
        with_button=with_button,
        custom_name=custom_name,
        sponsor=sponsor,
        price=price,
        message=message,
        end_time=endtime,
        start_time=starttime,
        new_message_requirement=new_message_requirement,
        day_requirement=day_requirement,
        channel_requirements=channel_requirements,
        role_requirement=role_requirement,
        voice_requirement=voice_requirement,
        channel_id=channel_id,
    )
    await giveaway_service.update(giveaway_id, params)


async def set_text_cooldown(guild_id: str, cooldown: int) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, text_cooldown=cooldown)


async def set_voice_cooldown(guild_id: str, cooldown: int) -> None:
    from repositories.level_config_repository import level_config_repo

    await level_config_repo.update_field(guild_id, voice_cooldown=cooldown)


async def get_text_cooldown(guild_id: str) -> int:
    """Get the text XP cooldown for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.text_cooldown


async def get_voice_cooldown(guild_id: str) -> int:
    """Get the voice XP cooldown for a guild, using cached config when available."""
    from repositories.level_config_repository import level_config_repo

    config = await level_config_repo.get_config(guild_id)
    return config.voice_cooldown


async def useToken(user_id: str, amount: int) -> None:
    query = """
    UPDATE aiToken
    SET freeToken = CASE
                        WHEN freeToken >= %s THEN freeToken - %s
                        ELSE freeToken
                    END,
        usedToken = CASE
                        WHEN freeToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE user_id = %s AND freeToken >= %s;
    UPDATE aiToken
    SET plusToken = CASE
                        WHEN freeToken < %s AND plusToken >= %s THEN plusToken - %s
                        ELSE plusToken
                    END,
        usedToken = CASE
                        WHEN freeToken < %s AND plusToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE user_id = %s AND freeToken < %s AND plusToken >= %s;
    UPDATE aiToken
    SET paidToken = CASE
                        WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN paidToken - %s
                        ELSE paidToken
                    END,
        usedToken = CASE
                        WHEN freeToken < %s AND plusToken < %s AND paidToken >= %s THEN usedToken + %s
                        ELSE usedToken
                    END
    WHERE user_id = %s AND freeToken < %s AND plusToken < %s AND paidToken >= %s;
    """
    params = (
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        amount,
        user_id,
        amount,
        amount,
        amount,
    )

    await execute_action(query, params)


async def addToken(user_id: str, amount: int) -> None:
    query = """
    INSERT INTO aiToken (user_id, paidToken)
    VALUES (%s, %s)
    ON DUPLICATE KEY
    UPDATE paidToken = paidToken + %s
    """
    params = (user_id, amount, amount)
    await execute_action(query, params)


async def getToken(user_id: str) -> int:
    query = "SELECT freeToken, plusToken, paidToken FROM aiToken WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    token = result[0] if result else None
    token_sum = token[0] + token[1] + token[2] if token else 0
    return token_sum


async def getTokenOverview(user_id: str) -> TokenOverviewModel | None:
    query = "SELECT freeToken, plusToken, paidToken, usedToken FROM aiToken WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return TokenOverviewModel.from_row(result[0]) if result else None


async def includeToToken(user_id: str) -> None:
    query = "INSERT INTO aiToken (user_id) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


async def resetToken(entitlements: list[Entitlement] | None = None) -> None:
    query = "UPDATE aiToken SET freeToken = 500"
    await execute_action(query)
    if entitlements is not None:
        for entitlement in entitlements:
            query2 = "UPDATE aiToken SET plusToken = 2000 WHERE user_id = %s"
            params2 = (str(entitlement.user_id),)
            await execute_action(query2, params2)


async def consumePaidToken(user_id: str, amount: int) -> None:
    query = "UPDATE aiToken SET paidToken = paidToken + %s WHERE user_id = %s"
    params = (amount, user_id)
    await execute_action(query, params)


async def getLevelLeaderboard(guild_id: str) -> AsyncIterator[LevelLeaderboardEntryModel]:
    """Stream the full level leaderboard for a guild.

    Yields rows one at a time, ordered by XP descending.
    """
    query = "SELECT user_id, xp FROM level WHERE guild_id = %s ORDER BY xp DESC"
    params = (guild_id,)
    async for row in LevelLeaderboardEntryModel.iter_rows(query, params):
        yield row


async def get_level_leaderboard_paginated(
    guild_id: str,
    limit: int = 10,
    offset: int = 0,
) -> list[LevelLeaderboardEntryModel]:
    """Fetch a paginated slice of the level leaderboard.

    Uses SQL-level LIMIT/OFFSET so only the requested page of rows
    is loaded from the database.
    """
    if limit < 1:
        limit = 10
    if offset < 0:
        offset = 0
    query = """
        SELECT user_id, xp FROM level
        WHERE guild_id = %s
        ORDER BY xp DESC, user_id ASC
        LIMIT %s OFFSET %s
    """
    params = (guild_id, limit, offset)
    rows: list[LevelLeaderboardEntryModel] = []
    async for row in LevelLeaderboardEntryModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_level_leaderboard_count(guild_id: str) -> int:
    """Return the total number of members on the leaderboard for a guild."""
    query = "SELECT COUNT(*) FROM level WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else 0


async def addCustomSituation(
    user_id: str,
    situation: str,
    name: str,
    temperature: float,
    top_p: float,
    frequency_penalty: float,
    presence_penalty: float,
) -> None:
    query = """
    INSERT INTO aiSituations (user_id, situation, name, temperature, top_p, frequency_penalty, presence_penalty)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        user_id,
        situation,
        name,
        temperature,
        top_p,
        frequency_penalty,
        presence_penalty,
    )
    return await execute_action(query, params)


async def getCustomSituations() -> list[str]:
    query = "SELECT name FROM aiSituations where unlocked = 1"
    result = await safe_execute_query(query)
    return [row[0] for row in result]


async def getCustomSituation(name: str) -> AISituationModel | None:
    query = "SELECT user_id, situation, name, created_at, temperature, top_p, frequency_penalty, presence_penalty, unlocked FROM aiSituations WHERE name = %s"
    params = (name,)
    result = await execute_query(query, params)
    return AISituationModel.from_row(result[0]) if result else None


async def getCustomSituationFromUser(user_id: str) -> AISituationModel | None:
    query = "SELECT user_id, situation, name, created_at, temperature, top_p, frequency_penalty, presence_penalty, unlocked FROM aiSituations WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return AISituationModel.from_row(result[0]) if result else None


async def deleteCustomSituation(user_id: str) -> None:
    query = "DELETE FROM aiSituations WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)


async def unlockCustomSituation(user_id: str) -> None:
    query = "UPDATE aiSituations SET unlocked = 1 WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)


async def addAutoPublish(channel_id: str) -> None:
    query = """
    INSERT INTO autopublish (channel_id)
    VALUES (%s)
    """
    params = (channel_id,)
    return await execute_action(query, params)


async def checkIfChannelIsAutopublish(channel_id: str) -> bool:
    query = "SELECT * FROM autopublish WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result is not None and len(result) > 0


async def removeAutoPublish(channel_id: str) -> None:
    query = "DELETE FROM autopublish WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def feedbackBlockUser(user_id: str) -> None:
    query = "INSERT INTO feedbackBlocked (user_id) VALUES (%s)"
    params = (user_id,)
    await execute_action(query, params)


async def feedbackUnblockUser(user_id: str) -> None:
    query = "DELETE FROM feedbackBlocked WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)


async def feedbackIsBlocked(user_id: str) -> bool:
    query = "SELECT * FROM feedbackBlocked WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result is not None and len(result) > 0


async def add_booster_channel(guild_id: str, channel_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    await booster_service.add(BoosterType.CHANNEL, guild_id, channel_id)


async def delete_booster_channel(guild_id: str, channel_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    await booster_service.delete(BoosterType.CHANNEL, guild_id, entity_id=channel_id)


async def get_booster_channel(guild_id: str) -> str | None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    return await booster_service.get(BoosterType.CHANNEL, guild_id)


async def claim_booster_channel(user_id: str, channel_id: str, guild_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    await booster_service.claim(ClaimedBoosterType.CHANNEL, user_id, channel_id, guild_id)


async def remove_claimed_booster_channel(user_id: str, guild_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    await booster_service.unclaim(ClaimedBoosterType.CHANNEL, user_id, guild_id)


async def get_claimed_booster_channel(
    user_id: str | None = None, guild_id: str | None = None
) -> str | list[ClaimedBoosterChannelModel] | None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    if user_id:
        claims = await booster_service.get_user_claims(ClaimedBoosterType.CHANNEL, user_id)
        if guild_id:
            # Filter to the specific guild and return the channel_id or None
            for claim in claims:
                if claim.guild_id == guild_id:
                    return claim.channel_id
            return None
        return claims or None
    return await booster_service.get_all_claims(ClaimedBoosterType.CHANNEL) or None


async def add_booster_role(guild_id: str, role_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    await booster_service.add(BoosterType.ROLE, guild_id, role_id)


async def get_booster_role(guild_id: str) -> str | None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    return await booster_service.get(BoosterType.ROLE, guild_id)


async def delete_booster_role(guild_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import BoosterType, booster_service

    await booster_service.delete(BoosterType.ROLE, guild_id)


async def add_claimed_booster_role(user_id: str, role_id: str, guild_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    await booster_service.claim(ClaimedBoosterType.ROLE, user_id, role_id, guild_id)


async def remove_claimed_booster_role(user_id: str, guild_id: str) -> None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    await booster_service.unclaim(ClaimedBoosterType.ROLE, user_id, guild_id)


async def get_claimed_booster_role(
    user_id: str | None = None, guild_id: str | None = None
) -> str | list[ClaimedBoosterRoleModel] | None:
    """Backward-compatible wrapper around BoosterService."""
    from services.booster_service import ClaimedBoosterType, booster_service

    if user_id:
        claims = await booster_service.get_user_claims(ClaimedBoosterType.ROLE, user_id)
        if guild_id:
            # Filter to the specific guild and return the role_id or None
            for claim in claims:
                if claim.guild_id == guild_id:
                    return claim.role_id
            return None
        return claims or None
    return await booster_service.get_all_claims(ClaimedBoosterType.ROLE) or None


async def set_log_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO log_channel (guild_id, channel_id) VALUES (%s, %s)"
    params: Any = (guild_id, channel_id)
    existing = await execute_query("SELECT 1 FROM log_enables WHERE guild_id = %s", (guild_id,))
    if not existing:
        query = "REPLACE INTO log_enables (guild_id) VALUES (%s)"
        params = (guild_id,)
    await execute_action(query, params)


async def remove_log_channel(guild_id: str) -> None:
    query = "DELETE FROM log_channel WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_log_channel(guild_id: str) -> str | None:
    query = "SELECT channel_id FROM log_channel WHERE guild_id = %s"
    params = (guild_id,)
    print("query: ", query)
    print("params: ", params)
    result = await execute_query(query, params)
    return result[0][0] if result else None


_LOG_ENABLE_COLUMNS = frozenset(
    {
        "guild_id",
        "automodRuleCreate",
        "automodRuleUpdate",
        "automodRuleDelete",
        "automodAction",
        "guild_channelDelete",
        "guild_channelCreate",
        "guild_channelUpdate",
        "guildUpdate",
        "inviteCreate",
        "inviteDelete",
        "memberJoin",
        "memberLeave",
        "memberUpdate",
        "userUpdate",
        "memberBan",
        "memberUnban",
        "presenceUpdate",
        "messageEdit",
        "messageDelete",
        "reactionAdd",
        "reactionRemove",
        "guildRoleCreate",
        "guildRoleDelete",
        "guildRoleUpdate",
    }
)


async def set_log_enable(guild_id: str, **kwargs: Any) -> None:
    query = "UPDATE log_enables SET "
    end_query = " WHERE guild_id = %s"
    params: list[Any] = []

    known_columns = LogEnableModel.known_db_columns()
    for key, value in kwargs.items():
        if value is not None and key in known_columns:
            query += f"{key} = %s, "
            params.append(value)

    if not params:
        return

    params.append(guild_id)
    query = query.rstrip(", ") + end_query

    await execute_action(query, tuple(params))


async def get_log_enable(guild_id: str | int) -> LogEnableModel:
    query = "SELECT guild_id, automodRuleCreate, automodRuleUpdate, automodRuleDelete, automodAction, guild_channelDelete, guild_channelCreate, guild_channelUpdate, guildUpdate, inviteCreate, inviteDelete, memberJoin, memberLeave, memberUpdate, userUpdate, memberBan, memberUnban, presenceUpdate, messageEdit, messageDelete, reactionAdd, reactionRemove, guildRoleCreate, guildRoleDelete, guildRoleUpdate FROM log_enables WHERE guild_id = %s"
    params = (str(guild_id),)
    result = await execute_query(query, params)
    if result and result[0]:
        return LogEnableModel.from_row(result[0])
    return LogEnableModel(
        guild_id=str(guild_id),
        automod_rule_create=True,
        automod_rule_update=True,
        automod_rule_delete=True,
        automod_action=False,
        guild_channel_delete=True,
        guild_channel_create=True,
        guild_channel_update=True,
        guild_update=True,
        invite_create=True,
        invite_delete=False,
        member_join=True,
        member_leave=True,
        member_update=True,
        user_update=True,
        member_ban=True,
        member_unban=True,
        presence_update=True,
        message_edit=True,
        message_delete=True,
        reaction_add=False,
        reaction_remove=False,
        guild_role_create=True,
        guild_role_delete=True,
        guild_role_update=True,
    )


async def add_scheduled_message(
    guild_id: str | None,
    channel_id: str | None,
    user_id: str,
    content: str,
    send_time: datetime,
    repeat_interval: int | None = None,
    repeat_amount: int | None = None,
    attachments: str | None = None,
) -> None:
    query = """
    INSERT INTO scheduledMessages
    (guild_id, channel_id, user_id, content, send_time, repeatInterval, repeatAmount, attachments)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (guild_id, channel_id, user_id, content, send_time, repeat_interval, repeat_amount, attachments)
    await execute_action(query, params)


async def get_scheduled_messages(user_id: str) -> list[ScheduledMessageModel]:
    query = """
    SELECT messageId, guild_id, channel_id, user_id, content, send_time, repeatInterval, repeatAmount, attachments, discord_message_id, created_at
    FROM scheduledMessages
    WHERE user_id = %s
    ORDER BY send_time ASC
    """
    params = (user_id,)
    rows: list[ScheduledMessageModel] = []
    async for row in ScheduledMessageModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def remove_scheduled_message(message_id: int) -> None:
    query = "DELETE FROM scheduledMessages WHERE messageId = %s"
    params = (message_id,)
    await execute_action(query, params)


async def get_user_scheduled_messages_in_timeframe(
    user_id: str,
    start_time: datetime,
    end_time: datetime,
    guild_id: str | None = None,
) -> list[ScheduledMessageModel]:
    query = """
    SELECT messageId, guild_id, channel_id, user_id, content, send_time, repeatInterval, repeatAmount, attachments, discord_message_id, created_at
    FROM scheduledMessages
    WHERE user_id = %s
    AND send_time BETWEEN %s AND %s
    """
    params: list[Any] = [user_id, start_time, end_time]

    if guild_id:
        query += " AND guild_id = %s"
        params.append(guild_id)

    rows: list[ScheduledMessageModel] = []
    async for row in ScheduledMessageModel.iter_rows(query, tuple(params)):
        rows.append(row)
    return rows


async def update_scheduled_message_content(message_id: int, new_content: str) -> None:
    query = "UPDATE scheduledMessages SET content = %s WHERE messageId = %s"
    params = (new_content, message_id)
    await execute_action(query, params)


async def update_scheduled_message_repeat_amount(message_id: int, repeat_amount: int) -> None:
    query = "UPDATE scheduledMessages SET repeatAmount = %s WHERE messageId = %s"
    params = (repeat_amount, message_id)
    await execute_action(query, params)


async def get_ready_scheduled_messages() -> list[ScheduledMessageModel]:
    query = """
    SELECT messageId, guild_id, channel_id, user_id, content, send_time, repeatInterval, repeatAmount, attachments, discord_message_id, created_at
    FROM scheduledMessages WHERE send_time <= NOW()
    """
    rows: list[ScheduledMessageModel] = []
    async for row in ScheduledMessageModel.iter_rows(query):
        rows.append(row)
    return rows


# Report functions have been moved to ReportService in services/report_service.py
# Import them from there for new code. Old aliases kept for backward compat.


async def report_user(
    guild_id: str,
    user_id: str,
    reporter_id: str,
    reason: str,
    is_moderator: bool = False,
) -> int | None:
    from services.report_service import ReportCreateParams
    from services.report_service import report_service as _report_svc

    return await _report_svc.create(
        ReportCreateParams(
            guild_id=guild_id,
            user_id=user_id,
            reporter_id=reporter_id,
            reason=reason,
            is_moderator=is_moderator,
        )
    )


async def accept_report(guild_id: str, report_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.accept(guild_id, report_id, accepted_by=None)


async def reject_report(guild_id: str, report_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.reject(guild_id, report_id, accepted_by=None)


async def resolve_report(guild_id: str, report_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.resolve(guild_id, report_id)


async def delete_report(guild_id: str, report_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.delete(guild_id, report_id)


async def get_reports(guild_id: str, user_id: str | None = None) -> list[ReportModel]:
    from services.report_service import ReportFilter
    from services.report_service import report_service as _report_svc

    return await _report_svc.get(ReportFilter(guild_id=guild_id, user_id=user_id))


async def get_reports_by_reporter(guild_id: str, reporter_id: str) -> list[ReportModel]:
    from services.report_service import report_service as _report_svc

    return await _report_svc.get_by_reporter(guild_id, reporter_id)


async def block_reporter(guild_id: str, reporter_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.block_reporter(guild_id, reporter_id)


async def unblock_reporter(guild_id: str, reporter_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.unblock_reporter(guild_id, reporter_id)


async def get_blocked_reporters(guild_id: str) -> list[BlockedReporterModel]:
    from services.report_service import report_service as _report_svc

    return await _report_svc.get_blocked_reporters(guild_id)


async def check_if_reporter_is_blocked(guild_id: str, reporter_id: str) -> bool:
    from services.report_service import report_service as _report_svc

    return await _report_svc.is_blocked(guild_id, reporter_id)


async def get_report_channel(guild_id: str) -> str | None:
    from services.report_service import report_service as _report_svc

    return await _report_svc.get_channel(guild_id)


async def set_report_channel(guild_id: str, channel_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.set_channel(guild_id, channel_id)


async def remove_report_channel(guild_id: str) -> None:
    from services.report_service import report_service as _report_svc

    await _report_svc.remove_channel(guild_id)


# ── Trigger message functions (delegated to TriggerMessageRepository) ──────────────
from repositories.trigger_message_repository import trigger_message_repo


async def get_trigger_messages(guild_id: str) -> list[TriggerMessageModel]:
    return await trigger_message_repo.get_all(guild_id)


async def add_trigger_message(guild_id: str, trigger: str, response: str, case_sensitive: bool = False) -> None:
    await trigger_message_repo.add(guild_id, trigger, response, case_sensitive)


async def remove_trigger_message(guild_id: str, trigger: str) -> None:
    await trigger_message_repo.remove(guild_id, trigger)


async def get_trigger_message_channels(guild_id: str, trigger_id: int) -> list[TriggerMessageChannelModel]:
    return await trigger_message_repo.get_channels(guild_id, trigger_id)


async def get_trigger_messages_by_channel(guild_id: str, channel_id: str) -> list[TriggerMessageChannelModel]:
    return await trigger_message_repo.get_by_channel(guild_id, channel_id)


async def add_trigger_message_channel(guild_id: str, channel_id: str, trigger_id: int) -> None:
    await trigger_message_repo.add_channel(guild_id, channel_id, trigger_id)


async def remove_trigger_message_channel(guild_id: str, channel_id: str, trigger_id: int) -> None:
    await trigger_message_repo.remove_channel(guild_id, channel_id, trigger_id)


async def is_trigger_message(guild_id: str, trigger: str, channel_id: str) -> TriggerMessageModel | None:
    return await trigger_message_repo.find(guild_id, trigger, channel_id)


# Ticket functions have been moved to TicketService in services/ticket_service.py
# Import them from there for new code. Old aliases kept for backward compat.


async def create_ticket_message(
    guild_id: str,
    channel_id: str,
    introduction: str,
    ping_role: str,
    name: str,
    description: str,
    summary_channel_id: str | None = None,
) -> int | None:
    from services.ticket_service import TicketMessageConfig
    from services.ticket_service import ticket_service as _ticket_svc

    return await _ticket_svc.create_config(
        TicketMessageConfig(
            guild_id=guild_id,
            channel_id=channel_id,
            introduction=introduction,
            ping_role=ping_role,
            name=name,
            description=description,
            summary_channel_id=summary_channel_id,
        )
    )


async def delete_ticket_message(guild_id: str, ticket_message_id: int) -> None:
    from services.ticket_service import ticket_service as _ticket_svc

    await _ticket_svc.delete_config(guild_id, ticket_message_id)


async def get_ticket_messages(guild_id: str) -> list[TicketMessageModel]:
    from services.ticket_service import ticket_service as _ticket_svc

    return await _ticket_svc.get_configs(guild_id)


async def get_ticket_messages_by_id(ticket_message_id: str) -> TicketMessageModel | None:
    from services.ticket_service import ticket_service as _ticket_svc

    try:
        message_id = int(ticket_message_id)
    except ValueError:
        return None
    return await _ticket_svc.get_config(message_id)


async def open_ticket(guild_id: str, opener_id: str, ticket_message_id: str, channel_id: str) -> None:
    from services.ticket_service import ticket_service as _ticket_svc

    try:
        message_id = int(ticket_message_id)
    except ValueError:
        return None
    await _ticket_svc.open(guild_id, opener_id, message_id, channel_id)


async def close_ticket(guild_id: str, channel_id: str, closed_by: str) -> None:
    from services.ticket_service import ticket_service as _ticket_svc

    try:
        cid = int(channel_id)
    except ValueError:
        return None
    await _ticket_svc.close(guild_id, cid, closed_by)


async def get_tickets(guild_id: str) -> list[TicketModel]:
    from services.ticket_service import ticket_service as _ticket_svc

    return await _ticket_svc.get_tickets(guild_id)


async def get_ticket_by_id(guild_id: str, ticket_id: str, channel_id: str) -> TicketModel | None:
    from services.ticket_service import ticket_service as _ticket_svc

    try:
        tid = int(ticket_id)
    except ValueError:
        return None
    return await _ticket_svc.get_by_config_and_channel(guild_id, tid, channel_id)


async def get_ticket_by_channel_id(guild_id: str, channel_id: str) -> TicketModel | None:
    from services.ticket_service import ticket_service as _ticket_svc

    return await _ticket_svc.get_by_channel(guild_id, channel_id)


async def get_join_to_create_channel(channel_id: str) -> bool:
    query = "SELECT 1 FROM join_to_create_channel WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return bool(result)


async def set_join_to_create_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO join_to_create_channel (guild_id, channel_id) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_join_to_create_channel(guild_id: str) -> None:
    query = "DELETE FROM join_to_create_channel WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_media_channel(channel_id: str) -> bool:
    query = "SELECT 1 FROM mediaChannel WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return bool(result)


async def add_media_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO mediaChannel (guild_id, channel_id) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_media_channel(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM mediaChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_welcome_channel(guild_id: str) -> WelcomeChannelModel | None:
    query = "SELECT channel_id, guild_id, message, imageBackground FROM welcome_channel WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return WelcomeChannelModel.from_row(result[0]) if result else None


async def set_welcome_channel(guild_id: str, channel_id: str, message: str, image_background: str) -> None:
    query = "INSERT INTO welcome_channel (guild_id, channel_id, message, imageBackground) VALUES (%s, %s, %s, %s)"
    params = (guild_id, channel_id, message, image_background)
    await execute_action(query, params)


async def remove_welcome_channel(guild_id: str) -> None:
    query = "DELETE FROM welcome_channel WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_leave_channel(guild_id: str) -> LeaveChannelModel | None:
    query = "SELECT channel_id, guild_id, message, imageBackground FROM leave_channel WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return LeaveChannelModel.from_row(result[0]) if result else None


async def set_leave_channel(guild_id: str, channel_id: str, message: str, image_background: str) -> None:
    query = "INSERT INTO leave_channel (guild_id, channel_id, message, imageBackground) VALUES (%s, %s, %s, %s)"
    params = (guild_id, channel_id, message, image_background)
    await execute_action(query, params)


async def remove_leave_channel(guild_id: str) -> None:
    query = "DELETE FROM leave_channel WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_dynamicslowmode_channels(guild_id: str) -> list[DynamicSlowmodeModel]:
    query = "SELECT guild_id, channel_id, messages, per, resetafter, cashedSlowmode FROM dynamicslowmode WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[DynamicSlowmodeModel] = []
    async for row in DynamicSlowmodeModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def add_dynamicslowmode(guild_id: str, channel_id: str, messages: int, per: int, resetafter: int) -> None:
    query = "INSERT INTO dynamicslowmode (guild_id, channel_id, messages, per, resetafter) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, channel_id, messages, per, resetafter)
    await execute_action(query, params)


async def remove_dynamicslowmode(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM dynamicslowmode WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_dynamicslowmode(channel_id: str) -> DynamicSlowmodeModel | None:
    query = "SELECT guild_id, channel_id, messages, per, resetafter, cashedSlowmode FROM dynamicslowmode WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return DynamicSlowmodeModel.from_row(result[0]) if result else None


async def add_dynamicslowmode_message(channel_id: str, message_id: str, send_time: datetime) -> None:
    query = "INSERT INTO dynamicslowmode_messages (channel_id, messageId, send_time) VALUES (%s, %s, %s)"
    params = (channel_id, message_id, send_time)
    await execute_action(query, params)


async def clear_old_dynamicslowmode_messages(channel_id: str, send_time: datetime) -> None:
    # Only delete messages older than the specified time, ensuring UTC comparison
    query = "DELETE FROM dynamicslowmode_messages WHERE channel_id = %s AND send_time < %s"
    params = (channel_id, send_time)
    await execute_action(query, params)


async def get_dynamicslowmode_messages(channel_id: str) -> list[DynamicSlowmodeMessageModel]:
    query = "SELECT id, channel_id, messageId, send_time FROM dynamicslowmode_messages WHERE channel_id = %s"
    params = (channel_id,)
    rows: list[DynamicSlowmodeMessageModel] = []
    async for row in DynamicSlowmodeMessageModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def cash_slowmode_delay(channel_id: str, slowmode_delay: int) -> None:
    query = "UPDATE dynamicslowmode SET cashedSlowmode = %s WHERE channel_id = %s"
    params = (slowmode_delay, channel_id)
    await execute_action(query, params)


async def remove_cashed_slowmode_delay(channel_id: str) -> None:
    query = "UPDATE dynamicslowmode SET cashedSlowmode = NULL WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


# ── Twitch notification functions (delegated to TwitchRepository) ──────────────────
from repositories.twitch_repository import twitch_repo


async def get_twitch_online_notification(channel_id: str) -> list[TwitchOnlineNotificationModel]:
    return await twitch_repo.get_by_channel(channel_id)


async def set_twitch_online_notification(
    guild_id: str,
    channel_id: str,
    twitch_uuid: str,
    twitch_name: str,
    notification_message: str,
) -> None:
    print("adding twitch online notification")
    await twitch_repo.set(guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
    print("added twitch online notification")


async def remove_twitch_online_notification(id: str) -> None:
    await twitch_repo.remove(id)


async def get_twitch_online_notification_by_twitch_uuid(twitch_uuid: str) -> TwitchOnlineNotificationModel | None:
    return await twitch_repo.get_by_twitch_uuid(twitch_uuid)


async def get_all_twitch_notification_uuids() -> list[str]:
    return await twitch_repo.get_all_uuids()


async def get_twitch_notification_by_guild_id(guild_id: str) -> list[TwitchOnlineNotificationModel]:
    return await twitch_repo.get_by_guild(guild_id)


async def get_brawlstars_linked_account(user_id: str) -> str | None:
    query = "SELECT brawlstarsTag FROM brawlstarsLinkedAccounts WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def add_brawlstars_linked_account(user_id: str, brawlstars_tag: str) -> None:
    query = "INSERT INTO brawlstarsLinkedAccounts (user_id, brawlstarsTag) VALUES (%s, %s)"
    params = (user_id, brawlstars_tag)
    await execute_action(query, params)


async def remove_brawlstars_linked_account(user_id: str) -> None:
    query = "DELETE FROM brawlstarsLinkedAccounts WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)
