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
    AfkMessageModel,
    AISituationModel,
    BlacklistEntryModel,
    BlockedReporterModel,
    ChannelOverwriteModel,
    ClaimedBoosterChannelModel,
    ClaimedBoosterRoleModel,
    CountingMode,
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
from utility import get_level_for_xp_async, get_xp_for_level_async

# Remove global pool and set_pool functions
# The pool will be accessed from the bot object

logger = logging.getLogger(__name__)

_bot = None


def set_bot(bot) -> None:
    global _bot
    _bot = bot


def _get_pool():
    if _bot and hasattr(_bot, "_pool") and _bot._pool is not None:
        return _bot._pool
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
    signals that are safe to replay.  Reads retry on connection/timeout/deadlock.
    """
    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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

_BLACKLIST_CACHE_TTL = 30  # seconds
_GUILD_CONFIG_CACHE_TTL = 300  # 5 minutes

_blacklist_cache: dict[str, tuple[Any, float]] = {}
_guild_config_cache: dict[str, tuple[dict[str, Any], float]] = {}
# In-memory cache for XP cooldowns: (guild_id, user_id) -> last_xp_gain_timestamp
# Eliminates DB queries entirely when user is on cooldown
_last_xp_gain_cache: dict[tuple[str, str], float] = {}


def _is_cache_valid(entry: tuple[Any, float] | None, ttl: float) -> bool:
    if entry is None:
        return False
    return (time.time() - entry[1]) < ttl


def _invalidate_guild_cache(guild_id: str) -> None:
    _blacklist_cache.pop(guild_id, None)
    _guild_config_cache.pop(guild_id, None)


async def preload_guild_configs(bot) -> None:
    """Fetch all guild-level configs at startup to warm the cache.

    Single bulk query replaces ~12+ individual queries per guild on first message.
    """
    query = """
    SELECT guild_id, active, difficulty, customFormula, level_up_messageActive,
           level_up_message, level_up_channel_id, textCooldown, voiceCooldown
    FROM levelConfig
    """
    pool = bot._pool if bot is not None and hasattr(bot, "_pool") and bot._pool is not None else _get_pool()
    if pool is None:
        return
    global _guild_config_cache
    _guild_config_cache = {}
    try:
        conn = await asyncio.wait_for(pool.acquire(), timeout=_POOL_ACQUIRE_TIMEOUT)
        async with conn, conn.cursor() as cursor:
            await asyncio.wait_for(cursor.execute(query), timeout=_QUERY_TIMEOUT)
            async for row in cursor:
                guild_id = str(row[0])
                _guild_config_cache[guild_id] = (
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
                    time.time(),
                )
    except Exception as e:
        print(f"Error preloading guild configs: {e}")


async def _get_cached_blacklist(guild_id: str) -> dict[str, list[BlacklistEntryModel]]:
    """Get blacklist with TTL cache (30s), reducing per-message DB queries by ~97%."""
    cached = _blacklist_cache.get(guild_id)
    if _is_cache_valid(cached, _BLACKLIST_CACHE_TTL):
        return cached[0]
    data = await get_blacklist(guild_id)
    _blacklist_cache[guild_id] = (data, time.time())
    return data


async def _get_cached_config(guild_id: str, key: str, default: Any = None) -> Any:
    """Get a cached level config value with TTL check. Falls back to DB on miss."""
    cache_entry = _guild_config_cache.get(guild_id)
    if _is_cache_valid(cache_entry, _GUILD_CONFIG_CACHE_TTL):
        return cache_entry[0].get(key, default)
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
                _guild_config_cache[guild_id] = (data, time.time())
                return data.get(key, default)
            # Cache the miss (no levelConfig row for this guild)
            _guild_config_cache[guild_id] = ({}, time.time())
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


async def execute_action(query: str, params: Any = None, bot=None) -> Any:
    async def _callback(cursor, connection):
        await connection.commit()
        return cursor.rowcount

    return await _execute_with_retry("execute_action", _callback, query, params, bot, is_write=True)


async def execute_batch(query: str, params_list: list[tuple], bot=None) -> None:
    """Execute a batch INSERT using executemany for bulk operations.

    Reduces database round-trips by sending all rows in one query.
    """
    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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


async def execute_insert_and_get_id(query: str, params: Any = None, bot=None) -> int | None:
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
    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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
            retryable = (
                "deadlock" in err_str
                or "connection" in err_str
                or "timeout" in err_str
            )
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
    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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
    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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


def get_table_definitions() -> dict[str, str]:
    """Return the table DDL definitions used by create_tables.

    Exported for testing purposes to avoid DDL duplication.
    """
    tables = {}
    tables["warnings"] = (
        "CREATE TABLE IF NOT EXISTS `warnings` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255),"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  `expires_at` TIMESTAMP NULL,"
        "  `created_by` VARCHAR(20) NOT NULL,"
        "  `escalation_level` INT DEFAULT 0"
        ") ENGINE=InnoDB"
    )
    tables["warn_config"] = (
        "CREATE TABLE IF NOT EXISTS `warn_config` ("
        "  `guild_id` VARCHAR(20) PRIMARY KEY,"
        "  `expiration_days` INT DEFAULT 0,"
        "  `timeout_threshold` INT DEFAULT 0,"
        "  `timeout_duration` INT DEFAULT 0,"
        "  `kick_threshold` INT DEFAULT 0,"
        "  `ban_threshold` INT DEFAULT 0"
        ") ENGINE=InnoDB"
    )
    tables["channel_overwrites"] = (
        "CREATE TABLE IF NOT EXISTS `channel_overwrites` ("
        "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `overwrites` JSON,"
        "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        ") ENGINE=InnoDB"
    )
    tables["message_tracking_opt_out"] = (
        "CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` (  `user_id` VARCHAR(20) PRIMARY KEY) ENGINE=InnoDB"
    )
    tables["counting"] = (
        "CREATE TABLE IF NOT EXISTS `counting` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT UNSIGNED DEFAULT 0,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["counting_challenge"] = (
        "CREATE TABLE IF NOT EXISTS `counting_challenge` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT UNSIGNED DEFAULT 0,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["counting_modes"] = (
        "CREATE TABLE IF NOT EXISTS `counting_modes` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `progress` INT DEFAULT 0,"
        "  `mode` TINYINT UNSIGNED DEFAULT 0,"
        "  `goal` INT,"
        "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["wordchain"] = (
        "CREATE TABLE IF NOT EXISTS `wordchain` ("
        "  `channel_id` VARCHAR(20) PRIMARY KEY,"
        "  `word` VARCHAR(1028) DEFAULT NULL,"
        "  `last_user_id` VARCHAR(20) DEFAULT NULL,"
        "  `guild_id` VARCHAR(20)"
        ") ENGINE=InnoDB"
    )
    tables["level"] = (
        "CREATE TABLE IF NOT EXISTS `level` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `xp` INT UNSIGNED DEFAULT 0,"
        "  `customBackground` VARCHAR(255) DEFAULT NULL,"
        "  `last_xp_gain` DATETIME DEFAULT NOW(),"
        "  `last_voice_xp_gain` DATETIME DEFAULT NOW(),"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklistedUser"] = (
        "CREATE TABLE IF NOT EXISTS `blacklistedUser` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklisted_role"] = (
        "CREATE TABLE IF NOT EXISTS `blacklisted_role` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["blacklistedChannel"] = (
        "CREATE TABLE IF NOT EXISTS `blacklistedChannel` ("
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `reason` VARCHAR(255) DEFAULT NULL,"
        "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`channel_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["userXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `userXpBoost` ("
        "  `user_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`user_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["roleXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `roleXpBoost` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["channelXpBoost"] = (
        "CREATE TABLE IF NOT EXISTS `channelXpBoost` ("
        "  `channel_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
        "  `additive` TINYINT(1) DEFAULT 0,"
        "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
        "  PRIMARY KEY(`channel_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["levelRole"] = (
        "CREATE TABLE IF NOT EXISTS `levelRole` ("
        "  `role_id` VARCHAR(20) NOT NULL,"
        "  `guild_id` VARCHAR(20) NOT NULL,"
        "  `level` INT UNSIGNED DEFAULT 0,"
        "  PRIMARY KEY(`role_id`, `guild_id`)"
        ") ENGINE=InnoDB"
    )
    tables["levelConfig"] = (
        "CREATE TABLE IF NOT EXISTS `levelConfig` ("
        "  `guild_id` VARCHAR(20) PRIMARY KEY,"
        "  `difficulty` ENUM('easy', 'medium', 'hard', 'extreme', 'custom') "
        "DEFAULT 'medium',"
        "  `customFormula` VARCHAR(255) DEFAULT NULL,"
        "  `level_up_messageActive` TINYINT(1) DEFAULT 1,"
        "  `level_up_message` VARCHAR(1000) DEFAULT NULL,"
        "  `level_up_channel_id` VARCHAR(20) DEFAULT NULL,"
        "  `active` TINYINT(1) DEFAULT 1,"
        "  `textCooldown` INT DEFAULT 60,"
        "  `voiceCooldown` INT DEFAULT 60"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
    )
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
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    tables["giveawayParticipant"] = """
    CREATE TABLE IF NOT EXISTS `giveawayParticipant` (
        `user_id` VARCHAR(20),
        `giveaway_id` INT UNSIGNED,
        PRIMARY KEY(`user_id`, `giveaway_id`)
    ) ENGINE=InnoDB;
    """
    tables["giveawayRoleRequirement"] = """
    CREATE TABLE IF NOT EXISTS `giveawayRoleRequirement` (
        `role_id` VARCHAR(20),
        `giveaway_id` INT UNSIGNED,
        PRIMARY KEY(`role_id`, `giveaway_id`)
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
    tables["giveawayBlacklistedRole"] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedRole` (
        `role_id` VARCHAR(20) PRIMARY KEY,
        `guild_id` VARCHAR(20),
        `reason` VARCHAR(255) DEFAULT NULL
    ) ENGINE=InnoDB;
    """
    tables["giveawayBlacklistedUser"] = """
    CREATE TABLE IF NOT EXISTS `giveawayBlacklistedUser` (
        `user_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        `reason` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY(`user_id`, `guild_id`)
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
    tables["aiToken"] = """
    CREATE TABLE IF NOT EXISTS `aiToken` (
        `freeToken` SMALLINT UNSIGNED DEFAULT 500,
        `plusToken` SMALLINT UNSIGNED DEFAULT 0,
        `paidToken` INT UNSIGNED DEFAULT 0,
        `usedToken` INT UNSIGNED DEFAULT 0,
        `user_id` VARCHAR(20) PRIMARY KEY
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
    tables["autopublish"] = """
    CREATE TABLE IF NOT EXISTS `autopublish` (
        `channel_id` VARCHAR(20) PRIMARY KEY
    ) ENGINE=InnoDB;
    """
    tables["feedbackBlocked"] = """
    CREATE TABLE IF NOT EXISTS `feedbackBlocked` (
        `user_id` VARCHAR(20) PRIMARY KEY
    ) ENGINE=InnoDB;
    """
    tables["afk_users"] = """
    CREATE TABLE IF NOT EXISTS `afk_users` (
        `user_id` VARCHAR(20) PRIMARY KEY,
        `reason` VARCHAR(1024)
    ) ENGINE=InnoDB;
    """
    tables["afkMessages"] = """
    CREATE TABLE IF NOT EXISTS `afkMessages` (
        `user_id` VARCHAR(20),
        `messageId` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`user_id`, `messageId`)
    ) ENGINE=InnoDB;
    """
    tables["booster_channel"] = """
    CREATE TABLE IF NOT EXISTS `booster_channel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
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
    tables["boosterRole"] = """
    CREATE TABLE IF NOT EXISTS `boosterRole` (
        `guild_id` VARCHAR(20),
        `role_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `role_id`)
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
    tables["log_channel"] = """
    CREATE TABLE IF NOT EXISTS `log_channel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["log_channel_blacklist"] = """
    CREATE TABLE IF NOT EXISTS `log_channel_blacklist` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["logRoleBlacklist"] = """
    CREATE TABLE IF NOT EXISTS `logRoleBlacklist` (
        `guild_id` VARCHAR(20),
        `role_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `role_id`)
    ) ENGINE=InnoDB;
    """
    tables["logBlacklistChannel"] = """
    CREATE TABLE IF NOT EXISTS `logBlacklistChannel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["logUserBlacklist"] = """
    CREATE TABLE IF NOT EXISTS `logUserBlacklist` (
        `guild_id` VARCHAR(20),
        `user_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `user_id`)
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
        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX `idx_sendtime` (send_time),
        INDEX `idx_user` (user_id),
        INDEX `idx_guild` (guild_id)
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
    tables["blockedReporters"] = """
    CREATE TABLE IF NOT EXISTS `blockedReporters` (
        `guild_id` VARCHAR(20),
        `user_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `user_id`)
    ) ENGINE=InnoDB;
    """
    tables["reportchannel"] = """
    CREATE TABLE IF NOT EXISTS `reportchannel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
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
    tables["join_to_create_channel"] = """
    CREATE TABLE IF NOT EXISTS `join_to_create_channel` (
        `guild_id` VARCHAR(20),
        `channel_id` VARCHAR(20),
        PRIMARY KEY(`guild_id`, `channel_id`)
    ) ENGINE=InnoDB;
    """
    tables["mediaChannel"] = """
    CREATE TABLE IF NOT EXISTS `mediaChannel` (
        `channel_id` VARCHAR(20),
        `guild_id` VARCHAR(20),
        PRIMARY KEY(`channel_id`)
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
    tables["brawlstarsLinkedAccounts"] = """
    CREATE TABLE IF NOT EXISTS `brawlstarsLinkedAccounts` (
        `user_id` VARCHAR(20),
        `brawlstarsTag` VARCHAR(20),
        PRIMARY KEY(`user_id`)
    ) ENGINE=InnoDB;
    """
    return tables


async def create_tables(bot=None) -> None:
    """Create all database tables using get_table_definitions()."""
    tables = get_table_definitions()

    pool = _get_pool() if bot is None else (bot._pool if hasattr(bot, "_pool") else None)
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
            name for name in to_create
            if all(dep in created or dep not in to_create for dep in dependencies.get(name, []))
        }
        if not batch:
            # Circular dependency or missing parent - shouldn't happen with current schema
            raise RuntimeError(f"Cannot resolve table dependencies for: {to_create}")
        batches.append(batch)
        to_create -= batch
        created.update(batch)

    # Create tables in batches, parallelizing within each batch
    for batch in batches:
        await asyncio.gather(
            *[execute_action(tables[table_name], bot=bot) for table_name in batch]
        )


async def add_warning(
    guild_id: str | int, user_id: str | int, reason: str, created_by: str | int, expiration_date: datetime | None = None
) -> int:
    query = "INSERT INTO warnings (guild_id, user_id, reason, expires_at, created_by) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, user_id, reason, expiration_date, created_by)
    warning_id = await execute_insert_and_get_id(query, params)
    return warning_id


async def get_warnings(guild_id: str | int, user_id: str | int | None = None) -> AsyncIterator[WarningModel]:
    """Stream all active warnings for a guild (or a specific user).

    Yields rows one at a time so that only one row is held in memory
    at a time, even when the result set contains thousands of warnings.
    """
    if user_id:
        query = "SELECT id, guild_id, user_id, reason, created_at, expires_at, created_by, escalation_level FROM warnings WHERE guild_id = %s AND user_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
        params = (guild_id, user_id)
    else:
        query = "SELECT id, guild_id, user_id, reason, created_at, expires_at, created_by, escalation_level FROM warnings WHERE guild_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
        params = (guild_id,)
    async for row in WarningModel.iter_rows(query, params):
        yield row


async def get_detailed_warnings(guild_id: str | int, user_id: str | int) -> AsyncIterator[DetailedWarningModel]:
    """Stream detailed warnings for a specific user in a guild.

    Yields rows one at a time, ordered by creation date descending.
    """
    query = (
        "SELECT id, reason, created_at, expires_at, created_by "
        "FROM warnings WHERE guild_id = %s AND user_id = %s "
        "ORDER BY created_at DESC"
    )
    params = (guild_id, user_id)
    async for row in DetailedWarningModel.iter_rows(query, params):
        yield row


async def remove_warning(warning_id: int) -> None:
    query = "DELETE FROM warnings WHERE id = %s"
    params = (warning_id,)
    await execute_action(query, params)


async def set_warn_config(
    guild_id: str | int,
    expiration_days: int,
    timeout_threshold: int,
    timeout_duration: int,
    kick_threshold: int,
    ban_threshold: int,
) -> None:
    query = (
        "INSERT INTO warn_config (guild_id, expiration_days, "
        "timeout_threshold, timeout_duration, "
        "kick_threshold, ban_threshold) "
        "VALUES (%s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE "
        "expiration_days = VALUES(expiration_days), "
        "timeout_threshold = VALUES(timeout_threshold), "
        "timeout_duration = VALUES(timeout_duration), "
        "kick_threshold = VALUES(kick_threshold), "
        "ban_threshold = VALUES(ban_threshold)"
    )
    params = (
        guild_id,
        expiration_days,
        timeout_threshold,
        timeout_duration,
        kick_threshold,
        ban_threshold,
    )
    await execute_action(query, params)


async def get_warn_config(guild_id: str | int) -> WarnConfigModel | None:
    query = "SELECT guild_id, expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold FROM warn_config WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    if result:
        return WarnConfigModel.from_row(result[0])
    else:
        return None


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


async def set_counting_progress(channel_id: str | int, progress: int, guild_id: str | int) -> None:
    query = "INSERT INTO counting (channel_id, progress, guild_id) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s"
    params = (channel_id, progress, guild_id, progress)
    await execute_action(query, params)


async def get_counting_channel_amount(guild_id: str | int) -> int:
    query = "SELECT COUNT(progress) FROM counting WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else 0


async def get_counting_progress(channel_id: str | int) -> int | None:
    query = "SELECT progress FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_counting_configs(channel_id: str | int) -> tuple[dict | None, dict | None, dict | None]:
    """Fetch all counting configs (normal, challenge, modes) for a channel in a single query.

    Returns (counting_config, challenge_config, modes_config) where each is a dict
    with keys like 'progress', 'last_counter_id', 'guild_id', or None if not configured.
    """
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
    return counting_config, challenge_config, modes_config


async def increase_counting_progress(channel_id: str | int, last_counter_id: str | int) -> None:
    query = "UPDATE counting SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(query, params)


async def get_last_counter_id(channel_id: str | int) -> str | None:
    query = "SELECT last_counter_id FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_counting(channel_id: str | int) -> None:
    query = "DELETE FROM counting WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def set_counting_challenge_progress(channel_id: str | int, progress: int) -> None:
    query = "INSERT INTO counting_challenge (channel_id, progress) VALUES (%s, %s) ON DUPLICATE KEY UPDATE progress = %s"
    params = (channel_id, progress, progress)
    await execute_action(query, params)


async def get_counting_challenge_progress(channel_id: str | int) -> int | None:
    query = "SELECT progress FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def increase_counting_challenge_progress(channel_id: Any, last_counter_id: Any) -> None:
    query = "UPDATE counting_challenge SET progress = progress + 1, last_counter_id = %s WHERE channel_id = %s"
    params = (last_counter_id, channel_id)
    await execute_action(query, params)


async def get_last_challenge_counter_id(channel_id: str | int) -> str | None:
    query = "SELECT last_counter_id FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_counting_challenge(channel_id: Any) -> None:
    query = "DELETE FROM counting_challenge WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def get_counting_challenge_channel_amount(guild_id: Any) -> int:
    query = "SELECT COUNT(progress) FROM counting_challenge WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else 0


async def set_counting_mode(channel_id: Any, progress: Any, mode: CountingMode, guild_id: Any) -> None:
    query = "INSERT INTO counting_modes (channel_id, progress, mode, guild_id) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = VALUES(progress), mode = VALUES(mode)"
    params = (channel_id, progress, mode, guild_id)
    await execute_action(query, params)


async def get_counting_mode_progress(channel_id: str | int) -> int | None:
    query = "SELECT progress FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_last_mode_counter_id(channel_id: str | int) -> str | None:
    query = "SELECT last_counter_id FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def clear_counting_mode(channel_id: Any) -> None:
    query = "DELETE FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    await execute_action(query, params)


async def get_counting_mode_mode(channel_id: str | int) -> CountingMode | None:
    query = "SELECT mode FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    if result and result[0][0] is not None:
        return CountingMode(result[0][0])
    return None


async def set_counting_mode_progress(
    channel_id: Any, progress: Any, guild_id: Any, mode: CountingMode, goal: Any, counter_id: Any
) -> None:
    query = "INSERT INTO counting_modes (channel_id, progress, guild_id, mode, goal, last_counter_id) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = %s, last_counter_id = %s"
    params = (
        channel_id,
        progress,
        guild_id,
        mode,
        goal,
        counter_id,
        progress,
        counter_id,
    )
    await execute_action(query, params)


async def get_count_mode_goal(channel_id: str | int) -> int | None:
    query = "SELECT goal FROM counting_modes WHERE channel_id = %s"
    params = (channel_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


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
    query = """
    INSERT INTO levelConfig (guild_id, active)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE active = VALUES(active)
    """
    params = (guild_id, active)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_level_system_status(guild_id: str) -> bool:
    """Check if the level system is enabled for a guild, using cached config when available."""
    cached_value = await _get_cached_config(guild_id, "active")
    if cached_value is not None:
        return cached_value
    query = "SELECT active FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else True


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
    query = """
    INSERT INTO levelConfig (guild_id, level_up_messageActive)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE level_up_messageActive = VALUES(level_up_messageActive)
    """
    params = (guild_id, status)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_levelup_message_status(guild_id: str) -> bool:
    """Get the level-up message status for a guild, using cached config when available."""
    cached_value = await _get_cached_config(guild_id, "level_up_message_active")
    if cached_value is not None:
        return cached_value
    query = "SELECT level_up_messageActive FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else True


async def set_levelup_message(guild_id: str, message: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, level_up_message)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE level_up_message = VALUES(level_up_message)
    """
    params = (guild_id, message)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_levelup_message(guild_id: str) -> str | None:
    """Get the level-up message for a guild, using cached config when available."""
    cached_value = await _get_cached_config(guild_id, "level_up_message")
    if cached_value is not None:
        return cached_value
    query = "SELECT level_up_message FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_levelup_channel(guild_id: str, channel_id: str | None) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, level_up_channel_id)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE level_up_channel_id = VALUES(level_up_channel_id)
    """
    params = (guild_id, channel_id)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_levelup_channel(guild_id: str) -> str | None:
    """Get the level-up channel for a guild, using cached config when available."""
    cached_value = await _get_cached_config(guild_id, "level_up_channel_id")
    if cached_value is not None:
        return cached_value
    query = "SELECT level_up_channel_id FROM levelConfig WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def set_xp_scaling(guild_id: str, scaling: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, difficulty)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE difficulty = VALUES(difficulty)
    """
    params = (guild_id, scaling)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_xp_scaling(guild_id: str) -> str:
    """Get the XP scaling for a guild, using cached config when available."""
    return await _get_cached_config(guild_id, "scaling", "medium")


async def set_custom_formula(guild_id: str, formula: str) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, customFormula)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE customFormula = VALUES(customFormula)
    """
    params = (guild_id, formula)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_custom_formula(guild_id: str) -> str | None:
    """Get the custom XP formula for a guild, using cached config when available."""
    return await _get_cached_config(guild_id, "custom_formula", None)


async def add_level_role(guild_id: str, role_id: str, level: int) -> None:
    query = """
    INSERT INTO levelRole (guild_id, role_id, level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
    """
    params = (guild_id, role_id, level)
    await execute_action(query, params)


async def get_level_roles(guild_id: str) -> AsyncIterator[LevelRoleModel]:
    """Stream level roles for a guild.

    Yields rows one at a time.
    """
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s"
    params = (guild_id,)
    async for row in LevelRoleModel.iter_rows(query, params):
        yield row


async def get_level_role(guild_id: str, role_id: str) -> int | None:
    query = "SELECT level FROM levelRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def remove_level_role(guild_id: str, role_id: str) -> None:
    query = """
    DELETE FROM levelRole
    WHERE guild_id = %s AND role_id = %s
    """
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_all_level_roles(guild_id: str) -> list[LevelRolesGroupModel]:
    query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s ORDER BY level"
    params = (guild_id,)
    groups: dict[int, list[str]] = {}
    async for row in execute_query_iter(query, params):
        level, role_id = row
        if level not in groups:
            groups[level] = []
        groups[level].append(role_id)
    return [LevelRolesGroupModel(level=level, role_ids=roles) for level, roles in groups.items()]


async def add_role_boost(guild_id: str, role_id: str, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO roleXpBoost (guild_id, role_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, role_id, boost, additive)
    await execute_action(query, params)


async def add_channel_boost(guild_id: str, channel_id: str, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO channelXpBoost (guild_id, channel_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, channel_id, boost, additive)
    await execute_action(query, params)


async def add_user_boost(guild_id: str, user_id: str, boost: float, additive: bool) -> None:
    query = """
    INSERT INTO userXpBoost (guild_id, user_id, boost, additive)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
    """
    params = (guild_id, user_id, boost, additive)
    await execute_action(query, params)


async def remove_role_boost(guild_id: str, role_id: str) -> None:
    query = "DELETE FROM roleXpBoost WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_channel_boost(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_user_boost(guild_id: str, user_id: str) -> None:
    query = "DELETE FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def get_all_boosts(guild_id: str) -> dict[str, list[XpBoostModel]]:
    role_query = "SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s"
    channel_query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s"
    user_query = "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s"

    roles: list[XpBoostModel] = []
    async for row in XpBoostModel.iter_rows(role_query, (guild_id,)):
        roles.append(row)

    channels: list[XpBoostModel] = []
    async for row in XpBoostModel.iter_rows(channel_query, (guild_id,)):
        channels.append(row)

    users: list[XpBoostModel] = []
    async for row in XpBoostModel.iter_rows(user_query, (guild_id,)):
        users.append(row)

    return {
        "roles": roles,
        "channels": channels,
        "users": users,
    }


async def get_user_boost(guild_id: str, user_id: str) -> XpBoostModel | None:
    query = "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await safe_execute_query(query, params)
    return XpBoostModel.from_row(result[0]) if result else None


async def get_user_roles_boosts(guild_id: str, role_ids: list[str]) -> list[XpBoostModel]:
    query = "SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s AND role_id IN %s"
    params = (guild_id, tuple(role_ids))
    rows: list[XpBoostModel] = []
    async for row in XpBoostModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_channel_boost(guild_id: str, channel_id: str) -> XpBoostModel | None:
    query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return XpBoostModel.from_row(result[0]) if result else None


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
    query = """
    INSERT INTO giveaway (
        guild_id, title, description, winners, withButton, customName, sponsor, price, message,
        endtime, starttime, newMessageRequirement, dayRequirement, voiceRequirement, channel_id
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )

    """
    params = (
        guild_id,
        title,
        description,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        endtime,
        starttime,
        new_message_requirement,
        day_requirement,
        voice_requirement,
        channel_id,
    )
    try:
        async with transaction() as conn, conn.cursor() as cursor:
            await cursor.execute(query, params)
            await cursor.execute("SELECT LAST_INSERT_ID()")
            last_id = await cursor.fetchone()
            giveaway_id = last_id[0] if last_id else None
            if giveaway_id is None:
                raise RuntimeError("Failed to get last insert ID for giveaway")

            if channel_requirements:
                channel_req_query = (
                    "INSERT INTO giveaway_channelRequirement (giveaway_id, channel_id, amount) VALUES (%s, %s, %s)"
                )
                channel_req_params = [(giveaway_id, ch_id, amount) for ch_id, amount in channel_requirements.items()]
                await cursor.executemany(channel_req_query, channel_req_params)

            if role_requirement:
                role_req_query = (
                    "INSERT INTO giveawayRoleRequirement (role_id, giveaway_id) VALUES (%s, %s)"
                )
                role_req_params = [(role_id, giveaway_id) for role_id in role_requirement]
                await cursor.executemany(role_req_query, role_req_params)
    except Exception as e:
        print(f"Error creating giveaway: {e}")
        return None

    return giveaway_id


async def set_giveaway_message_id(giveaway_id: int, message_id: int) -> None:
    query = "UPDATE giveaway SET messageId = %s WHERE giveaway_id = %s"
    params = (message_id, giveaway_id)
    await execute_action(query, params)


async def get_giveaway(giveaway_id: int) -> GiveawayModel | None:
    query = (
        "SELECT giveaway_id, guild_id, title, description, winners, withButton, "
        "customName, sponsor, price, message, endtime, starttime, started, ended, "
        "newMessageRequirement, dayRequirement, voiceRequirement, sendFailed, "
        "channel_id, messageId, created_at "
        "FROM giveaway WHERE giveaway_id = %s"
    )
    params = (giveaway_id,)
    result = await safe_execute_query(query, params)
    return GiveawayModel.from_row(result[0]) if result else None


async def get_giveaway_channel_requirements(giveaway_id: int) -> list[GiveawayChannelRequirementModel]:
    query = "SELECT channel_id, amount FROM giveaway_channelRequirement WHERE giveaway_id = %s"
    params = (giveaway_id,)
    rows: list[GiveawayChannelRequirementModel] = []
    async for row in GiveawayChannelRequirementModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_giveaway_role_requirements(giveaway_id: int) -> list[str]:
    query = "SELECT role_id FROM giveawayRoleRequirement WHERE giveaway_id = %s"
    params = (giveaway_id,)
    role_ids: list[str] = []
    async for row in execute_query_iter(query, params):
        role_ids.append(row[0])
    return role_ids


async def set_giveaway_started(giveaway_id: int) -> None:
    query = "UPDATE giveaway SET started = 1 WHERE giveaway_id = %s"
    params = (giveaway_id,)
    await execute_action(query, params)


async def set_giveaway_ended(giveaway_id: int) -> None:
    query = "UPDATE giveaway SET ended = 1 WHERE giveaway_id = %s"
    params = (giveaway_id,)
    await execute_action(query, params)


async def delete_old_giveaways() -> None:
    """Delete old ended giveaways and their related data in a single transaction."""
    try:
        async with transaction() as conn, conn.cursor() as cursor:
            # Find old giveaways first
            await cursor.execute("SELECT giveaway_id FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK")
            old_ids = [row[0] for row in await cursor.fetchall()]
            if not old_ids:
                return

            related_tables = [
                "giveaway_channelRequirement",
                "giveawayRoleRequirement",
                "giveawayParticipant",
                "giveawayVoiceTime",
                "giveawayNewMessage",
                "giveaway_channelMessages",
            ]
            for give_id in old_ids:
                for table in related_tables:
                    await cursor.execute(f"DELETE FROM {table} WHERE giveaway_id = %s", (give_id,))
            await cursor.execute("DELETE FROM giveaway WHERE ended = 1 AND endtime < NOW() - INTERVAL 1 WEEK")
    except Exception as e:
        print(f"Error deleting old giveaways: {e}")
        raise


async def get_giveaway_participants(giveaway_id: int) -> list[str]:
    query = "SELECT user_id FROM giveawayParticipant WHERE giveaway_id = %s"
    params = (giveaway_id,)
    user_ids: list[str] = []
    async for row in execute_query_iter(query, params):
        user_ids.append(row[0])
    return user_ids


async def get_new_messages(giveaway_id: int, user_id: str) -> int | None:
    query = "SELECT messages FROM giveawayNewMessage WHERE giveaway_id = %s AND user_id = %s"
    params = (giveaway_id, user_id)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def get_new_messages_channel(giveaway_id: int, channel_id: str, user_id: str) -> int | None:
    query = "SELECT amount FROM giveaway_channelMessages WHERE giveaway_id = %s AND channel_id = %s AND user_id = %s"
    params = (giveaway_id, channel_id, user_id)
    result = await safe_execute_query(query, params)
    return result[0][0] if result else None


async def get_voice_time(giveaway_id: int, user_id: str) -> int | None:
    query = "SELECT voiceMinutes FROM giveawayVoiceTime WHERE giveaway_id = %s AND user_id = %s"
    params = (giveaway_id, user_id)
    result = await safe_execute_query(query, params)
    return result[0][0] if result else None


async def get_blacklisted_roles(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    query = "SELECT role_id, reason FROM giveawayBlacklistedRole WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[GiveawayBlacklistEntryModel] = []
    async for row in GiveawayBlacklistEntryModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def check_if_user_blacklisted(guild_id: str, user_id: str) -> bool:
    query = "SELECT * FROM giveawayBlacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result is not None and len(result) > 0


async def check_if_giveaway_participant(giveaway_id: int, user_id: str) -> bool:
    query = "SELECT * FROM giveawayParticipant WHERE giveaway_id = %s AND user_id = %s"
    params = (giveaway_id, user_id)
    result = await safe_execute_query(query, params)
    return result is not None and len(result) > 0


async def remove_giveaway_participant(giveaway_id: int, user_id: str) -> None:
    query = "DELETE FROM giveawayParticipant WHERE giveaway_id = %s AND user_id = %s"
    params = (giveaway_id, user_id)
    await execute_action(query, params)


async def add_giveaway_participant(giveaway_id: int, user_id: str) -> None:
    query = "INSERT INTO giveawayParticipant (user_id, giveaway_id) VALUES (%s, %s)"
    params = (user_id, giveaway_id)
    await execute_action(query, params)


async def get_send_ready_giveaways() -> list[int]:
    query = "SELECT giveaway_id FROM giveaway WHERE started = 0 AND starttime < NOW()"
    giveaway_ids: list[int] = []
    async for row in execute_query_iter(query):
        giveaway_ids.append(row[0])
    return giveaway_ids


async def add_giveaway_voice_minutes_if_needed(user_id: Any, guild_id: Any) -> None:
    query = """
        INSERT INTO giveawayVoiceTime (giveaway_id, user_id, voiceMinutes)
        SELECT giveaway_id, %s, 1 FROM giveaway
        WHERE guild_id = %s AND voiceRequirement IS NOT NULL
        ON DUPLICATE KEY UPDATE voiceMinutes = voiceMinutes + 1
    """
    await execute_action(query, (user_id, guild_id))


async def add_giveaway_new_message_if_needed(user_id: Any, guild_id: Any) -> None:
    query = """
        INSERT INTO giveawayNewMessage (giveaway_id, user_id, messages)
        SELECT giveaway_id, %s, 1 FROM giveaway
        WHERE guild_id = %s AND newMessageRequirement IS NOT NULL
        ON DUPLICATE KEY UPDATE messages = messages + 1
    """
    await execute_action(query, (user_id, guild_id))


async def add_giveaway_new_message_channel_if_needed(user_id: Any, guild_id: Any, channel_id: Any) -> None:
    query = """
        INSERT INTO giveaway_channelMessages (giveaway_id, channel_id, user_id, amount)
        SELECT giveaway_id, %s, %s, 1 FROM giveaway
        WHERE guild_id = %s AND newMessageRequirement IS NOT NULL
        ON DUPLICATE KEY UPDATE amount = amount + 1
    """
    await execute_action(query, (channel_id, user_id, guild_id))


async def get_end_ready_giveaways() -> list[int]:
    query = "SELECT giveaway_id FROM giveaway WHERE ended = 0 AND endtime < NOW() AND started = 1 AND messageId <> 'pending'"
    giveaway_ids: list[int] = []
    async for row in execute_query_iter(query):
        giveaway_ids.append(row[0])
    return giveaway_ids


async def add_giveaway_blacklisted_user(guild_id: str, user_id: str) -> None:
    query = "INSERT INTO giveawayBlacklistedUser (guild_id, user_id) VALUES (%s, %s)"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def add_giveaway_blacklisted_role(guild_id: str, role_id: str) -> None:
    query = "INSERT INTO giveawayBlacklistedRole (guild_id, role_id) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_giveaway_blacklisted_user(guild_id: str, user_id: str) -> None:
    query = "DELETE FROM giveawayBlacklistedUser WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def remove_giveaway_blacklisted_role(guild_id: str, role_id: str) -> None:
    query = "DELETE FROM giveawayBlacklistedRole WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_giveaway_blacklisted_users(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    query = "SELECT user_id, reason FROM giveawayBlacklistedUser WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[GiveawayBlacklistEntryModel] = []
    async for row in GiveawayBlacklistEntryModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_giveaway_blacklisted_roles(guild_id: str) -> list[GiveawayBlacklistEntryModel]:
    query = "SELECT role_id, reason FROM giveawayBlacklistedRole WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[GiveawayBlacklistEntryModel] = []
    async for row in GiveawayBlacklistEntryModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def delete_giveaway(giveaway_id: int) -> None:
    """Delete a giveaway and all related data in a single transaction."""
    related_tables = [
        "giveaway_channelRequirement",
        "giveawayRoleRequirement",
        "giveawayParticipant",
        "giveawayVoiceTime",
        "giveawayNewMessage",
        "giveaway_channelMessages",
    ]
    try:
        async with transaction() as conn, conn.cursor() as cursor:
            for table in related_tables:
                await cursor.execute(f"DELETE FROM {table} WHERE giveaway_id = %s", (giveaway_id,))
            await cursor.execute("DELETE FROM giveaway WHERE giveaway_id = %s", (giveaway_id,))
    except Exception as e:
        print(f"Error deleting giveaway {giveaway_id}: {e}")
        raise


async def set_giveaway_endtime(giveaway_id: int, endtime: datetime) -> None:
    query = "UPDATE giveaway SET endtime = %s WHERE giveaway_id = %s"
    params = (endtime, giveaway_id)
    await execute_action(query, params)


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
    query = """
    UPDATE giveaway SET
        guild_id = %s,
        title = %s,
        description = %s,
        winners = %s,
        withButton = %s,
        customName = %s,
        sponsor = %s,
        price = %s,
        message = %s,
        endtime = %s,
        starttime = %s,
        newMessageRequirement = %s,
        dayRequirement = %s,
        voiceRequirement = %s,
        channel_id = %s
    WHERE giveaway_id = %s
    """
    params = (
        guild_id,
        title,
        description,
        winners,
        with_button,
        custom_name,
        sponsor,
        price,
        message,
        endtime,
        starttime,
        new_message_requirement,
        day_requirement,
        voice_requirement,
        channel_id,
        giveaway_id,
    )
    try:
        async with transaction() as conn, conn.cursor() as cursor:
            await cursor.execute(query, params)
            await cursor.execute(
                "DELETE FROM giveaway_channelRequirement WHERE giveaway_id = %s",
                (giveaway_id,),
            )
            if channel_requirements is not None and len(channel_requirements) > 0 and channel_requirements != {}:
                for ch_id, amount in channel_requirements.items():
                    await cursor.execute(
                        "INSERT INTO giveaway_channelRequirement (giveaway_id, channel_id, amount) VALUES (%s, %s, %s)",
                        (giveaway_id, ch_id, amount),
                    )
            await cursor.execute(
                "DELETE FROM giveawayRoleRequirement WHERE giveaway_id = %s",
                (giveaway_id,),
            )
            for role_id in role_requirement:
                await cursor.execute(
                    "INSERT INTO giveawayRoleRequirement (role_id, giveaway_id) VALUES (%s, %s)",
                    (role_id, giveaway_id),
                )
    except Exception as e:
        print(f"Error during giveaway update for {giveaway_id}: {e}")


async def set_text_cooldown(guild_id: str, cooldown: int) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, textCooldown)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE textCooldown = VALUES(textCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def set_voice_cooldown(guild_id: str, cooldown: int) -> None:
    query = """
    INSERT INTO levelConfig (guild_id, voiceCooldown)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE voiceCooldown = VALUES(voiceCooldown)
    """
    params = (guild_id, cooldown)
    await execute_action(query, params)
    _invalidate_guild_cache(guild_id)


async def get_text_cooldown(guild_id: str) -> int:
    """Get the text XP cooldown for a guild, using cached config when available."""
    return await _get_cached_config(guild_id, "text_cooldown", 60)


async def get_voice_cooldown(guild_id: str) -> int:
    """Get the voice XP cooldown for a guild, using cached config when available."""
    return await _get_cached_config(guild_id, "voice_cooldown", 60)


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


async def setAfk(user_id: str, reason: str) -> None:
    query = """
    INSERT INTO afk_users (user_id, reason)
    VALUES (%s, %s)
    """
    params = (user_id, reason)
    await execute_action(query, params)


async def removeAfk(user_id: str) -> None:
    query = "DELETE FROM afk_users WHERE user_id = %s"
    params = (user_id,)
    await execute_action(query, params)
    query = "DELETE FROM afkMessages WHERE user_id = %s"
    await execute_action(query, params)


async def checkIfUserIsAfk(user_id: str) -> bool:
    query = "SELECT * FROM afk_users WHERE user_id = %s"
    params = (user_id,)
    result = await safe_execute_query(query, params)
    return result is not None and len(result) > 0


async def addAfkMessage(user_id: str, message_id: str, channel_id: str) -> None:
    query = """
    INSERT INTO afkMessages (user_id, messageId, channel_id)
    VALUES (%s, %s, %s)
    """
    params = (user_id, message_id, channel_id)
    await execute_action(query, params)


async def getAfkMessages(user_id: str) -> list[AfkMessageModel]:
    query = "SELECT messageId, channel_id FROM afkMessages WHERE user_id = %s"
    params = (user_id,)
    rows: list[AfkMessageModel] = []
    async for row in AfkMessageModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def getAfkReason(user_id: str) -> str | None:
    query = "SELECT reason FROM afk_users WHERE user_id = %s"
    params = (user_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def add_booster_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO booster_channel (guild_id, channel_id) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def delete_booster_channel(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM booster_channel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_booster_channel(guild_id: str) -> str | None:
    query = "SELECT channel_id FROM booster_channel WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def claim_booster_channel(user_id: str, channel_id: str, guild_id: str) -> None:
    query = "INSERT INTO claimedBoosterChannel (user_id, channel_id, guild_id) VALUES (%s, %s, %s)"
    params = (user_id, channel_id, guild_id)
    await execute_action(query, params)


async def remove_claimed_booster_channel(user_id: str, guild_id: str) -> None:
    query = "DELETE FROM claimedBoosterChannel WHERE user_id = %s AND guild_id = %s"
    params = (user_id, guild_id)
    await execute_action(query, params)


async def get_claimed_booster_channel(
    user_id: str | None = None, guild_id: str | None = None
) -> str | list[ClaimedBoosterChannelModel] | None:
    if user_id:
        query = (
            "SELECT channel_id FROM claimedBoosterChannel WHERE user_id = %s AND guild_id = %s"
            if guild_id
            else "SELECT user_id, channel_id, guild_id FROM claimedBoosterChannel WHERE user_id = %s"
        )
        params = (user_id, guild_id) if guild_id else (user_id,)
        result = await safe_execute_query(query, params)
        if not result:
            return None
        return result[0][0] if guild_id else [ClaimedBoosterChannelModel.from_row(row) for row in result]
    else:
        query = "SELECT user_id, channel_id, guild_id FROM claimedBoosterChannel"
        result = await safe_execute_query(query)
        return [ClaimedBoosterChannelModel.from_row(row) for row in result]


async def add_booster_role(guild_id: str, role_id: str) -> None:
    query = "INSERT INTO boosterRole (guild_id, role_id) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_booster_role(guild_id: str) -> str | None:
    query = "SELECT role_id FROM boosterRole WHERE guild_id = %s"
    params = (guild_id,)
    result = await execute_query(query, params)
    return result[0][0] if result else None


async def delete_booster_role(guild_id: str) -> None:
    query = "DELETE FROM boosterRole WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def add_claimed_booster_role(user_id: str, role_id: str, guild_id: str) -> None:
    query = "INSERT INTO claimedBoosterRole (user_id, role_id, guild_id) VALUES (%s, %s, %s)"
    params = (user_id, role_id, guild_id)
    await execute_action(query, params)


async def remove_claimed_booster_role(user_id: str, guild_id: str) -> None:
    query = "DELETE FROM claimedBoosterRole WHERE user_id = %s AND guild_id = %s"
    params = (user_id, guild_id)
    await execute_action(query, params)


async def get_claimed_booster_role(
    user_id: str | None = None, guild_id: str | None = None
) -> str | list[ClaimedBoosterRoleModel] | None:
    if user_id:
        query = (
            "SELECT role_id FROM claimedBoosterRole WHERE user_id = %s AND guild_id = %s"
            if guild_id
            else "SELECT user_id, role_id, guild_id FROM claimedBoosterRole WHERE user_id = %s"
        )
        params = (user_id, guild_id) if guild_id else (user_id,)
        result = await safe_execute_query(query, params)
        if not result:
            return None
        return result[0][0] if guild_id else [ClaimedBoosterRoleModel.from_row(row) for row in result]
    else:
        query = "SELECT user_id, role_id, guild_id FROM claimedBoosterRole"
        result = await safe_execute_query(query)
        return [ClaimedBoosterRoleModel.from_row(row) for row in result]


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


async def add_log_blacklist_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO logBlacklistChannel (guild_id, channel_id) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_log_blacklist_channel(guild_id: str, channel_id: str) -> None:
    query = "DELETE FROM logBlacklistChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def get_log_blacklist_channel(guild_id: str) -> list[str]:
    query = "SELECT channel_id FROM logBlacklistChannel WHERE guild_id = %s"
    params = (guild_id,)
    channel_ids: list[str] = []
    async for row in execute_query_iter(query, params):
        channel_ids.append(row[0])
    return channel_ids


async def is_log_channel_blacklisted(guild_id: str, channel_id: str) -> str | None:
    query = "SELECT channel_id FROM logBlacklistChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_log_role_blacklist(guild_id: str, role_id: str) -> None:
    query = "INSERT INTO logRoleBlacklist (guild_id, role_id) VALUES (%s, %s)"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def remove_log_role_blacklist(guild_id: str, role_id: str) -> None:
    query = "DELETE FROM logRoleBlacklist WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    await execute_action(query, params)


async def get_log_role_blacklist(guild_id: str) -> list[str]:
    query = "SELECT role_id FROM logRoleBlacklist WHERE guild_id = %s"
    params = (guild_id,)
    role_ids: list[str] = []
    async for row in execute_query_iter(query, params):
        role_ids.append(row[0])
    return role_ids


async def is_log_role_blacklisted(guild_id: str, role_id: str) -> str | None:
    query = "SELECT role_id FROM logRoleBlacklist WHERE guild_id = %s AND role_id = %s"
    params = (guild_id, role_id)
    result = await execute_query(query, params)
    return result[0] if result else None


async def add_log_user_blacklist(guild_id: str, user_id: str) -> None:
    query = "INSERT INTO logUserBlacklist (guild_id, user_id) VALUES (%s, %s)"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def remove_log_user_blacklist(guild_id: str, user_id: str) -> None:
    query = "DELETE FROM logUserBlacklist WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    await execute_action(query, params)


async def get_log_user_blacklist(guild_id: str) -> list[str]:
    query = "SELECT user_id FROM logUserBlacklist WHERE guild_id = %s"
    params = (guild_id,)
    user_ids: list[str] = []
    async for row in execute_query_iter(query, params):
        user_ids.append(row[0])
    return user_ids


async def is_log_user_blacklisted(guild_id: str, user_id: str) -> str | None:
    query = "SELECT user_id FROM logUserBlacklist WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, user_id)
    result = await execute_query(query, params)
    return result[0] if result else None


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


async def report_user(
    guild_id: str,
    user_id: str,
    reporter_id: str,
    reason: str,
    is_moderator: bool = False,
) -> int | None:
    if is_moderator:
        query = "INSERT INTO reports (guild_id, user_id, reporterId, reason, accepted, accepted_at, acceptedBy) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        params: Any = (
            guild_id,
            user_id,
            reporter_id,
            reason,
            1,
            datetime.now(),
            reporter_id,
        )
    else:
        query = "INSERT INTO reports (guild_id, user_id, reporterId, reason) VALUES (%s, %s, %s, %s)"
        params = (guild_id, user_id, reporter_id, reason)
    report_id = await execute_action(query, params)
    return report_id


async def accept_report(guild_id: str, report_id: str) -> None:
    query = "UPDATE reports SET accepted = 1, accepted_at = NOW(), acceptedBy = %s WHERE id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def reject_report(guild_id: str, report_id: str) -> None:
    query = "UPDATE reports SET accepted = 0, accepted_at = NOW(), acceptedBy = %s WHERE id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def resolve_report(guild_id: str, report_id: str) -> None:
    query = "UPDATE reports SET resolved = 1 WHERE guild_id = %s AND id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def delete_report(guild_id: str, report_id: str) -> None:
    query = "DELETE FROM reports WHERE guild_id = %s AND id = %s"
    params = (guild_id, report_id)
    await execute_action(query, params)


async def get_reports(guild_id: str, user_id: str | None = None) -> list[ReportModel]:
    query = """
        SELECT id, guild_id, user_id, reporterId, reason,
               UNIX_TIMESTAMP(created_at) as created_at,
               accepted,
               UNIX_TIMESTAMP(accepted_at) as accepted_at,
               acceptedBy,
               resolved,
               UNIX_TIMESTAMP(resolved_at) as resolved_at,
               resolvedBy
        FROM reports WHERE guild_id = %s
    """
    params: list[Any] = [guild_id]
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)

    rows: list[ReportModel] = []
    async for row in ReportModel.iter_rows(query, tuple(params)):
        rows.append(row)
    return rows


async def get_reports_by_reporter(guild_id: str, reporter_id: str) -> list[ReportModel]:
    query = """
        SELECT id, guild_id, user_id, reporterId, reason,
               UNIX_TIMESTAMP(created_at) as created_at,
               accepted,
               UNIX_TIMESTAMP(accepted_at) as accepted_at,
               acceptedBy,
               resolved,
               UNIX_TIMESTAMP(resolved_at) as resolved_at,
               resolvedBy
        FROM reports WHERE guild_id = %s AND reporterId = %s
    """
    params = (guild_id, reporter_id)
    rows: list[ReportModel] = []
    async for row in ReportModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def block_reporter(guild_id: str, reporter_id: str) -> None:
    query = "INSERT INTO blockedReporters (guild_id, user_id) VALUES (%s, %s)"
    params = (guild_id, reporter_id)
    await execute_action(query, params)


async def unblock_reporter(guild_id: str, reporter_id: str) -> None:
    query = "DELETE FROM blockedReporters WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, reporter_id)
    await execute_action(query, params)


async def get_blocked_reporters(guild_id: str) -> list[BlockedReporterModel]:
    query = "SELECT guild_id, user_id FROM blockedReporters WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[BlockedReporterModel] = []
    async for row in BlockedReporterModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def check_if_reporter_is_blocked(guild_id: str, reporter_id: str) -> bool:
    query = "SELECT 1 FROM blockedReporters WHERE guild_id = %s AND user_id = %s"
    params = (guild_id, reporter_id)
    result = await execute_query(query, params)
    return bool(result)


async def get_report_channel(guild_id: str) -> str | None:
    result = await execute_query("SELECT channel_id FROM reportchannel WHERE guild_id = %s", (guild_id,))
    return result[0] if result else None


async def set_report_channel(guild_id: str, channel_id: str) -> None:
    query = "INSERT INTO reportchannel (guild_id, channel_id) VALUES (%s, %s)"
    params = (guild_id, channel_id)
    await execute_action(query, params)


async def remove_report_channel(guild_id: str) -> None:
    query = "DELETE FROM reportchannel WHERE guild_id = %s"
    params = (guild_id,)
    await execute_action(query, params)


async def get_trigger_messages(guild_id: str) -> list[TriggerMessageModel]:
    query = "SELECT id, guild_id, `trigger`, response, case_sensitive FROM triggerMessages WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[TriggerMessageModel] = []
    async for row in TriggerMessageModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def add_trigger_message(guild_id: str, trigger: str, response: str, case_sensitive: bool = False) -> None:
    query = "INSERT INTO triggerMessages (guild_id, `trigger`, response, case_sensitive) VALUES (%s, %s, %s, %s)"
    params = (guild_id, trigger, response, case_sensitive)
    await execute_action(query, params)


async def remove_trigger_message(guild_id: str, trigger: str) -> None:
    query = "DELETE FROM triggerMessages WHERE guild_id = %s AND `trigger` = %s"
    params = (guild_id, trigger)
    await execute_action(query, params)


async def get_trigger_message_channels(guild_id: str, trigger_id: int) -> list[TriggerMessageChannelModel]:
    query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND triggerId = %s"
    params = (guild_id, trigger_id)
    rows: list[TriggerMessageChannelModel] = []
    async for row in TriggerMessageChannelModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_trigger_messages_by_channel(guild_id: str, channel_id: str) -> list[TriggerMessageChannelModel]:
    query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s"
    params = (guild_id, channel_id)
    rows: list[TriggerMessageChannelModel] = []
    async for row in TriggerMessageChannelModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def add_trigger_message_channel(guild_id: str, channel_id: str, trigger_id: int) -> None:
    query = "INSERT INTO triggerMessagesChannel (guild_id, channel_id, triggerId) VALUES (%s, %s, %s)"
    params = (guild_id, channel_id, trigger_id)
    await execute_action(query, params)


async def remove_trigger_message_channel(guild_id: str, channel_id: str, trigger_id: int) -> None:
    query = "DELETE FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s AND triggerId = %s"
    params = (guild_id, channel_id, trigger_id)
    await execute_action(query, params)


async def is_trigger_message(guild_id: str, trigger: str, channel_id: str) -> TriggerMessageModel | None:
    query = """
        SELECT t.id, t.guild_id, t.`trigger`, t.response, t.case_sensitive FROM triggerMessages t
        LEFT JOIN triggerMessagesChannel tc ON t.id = tc.triggerId AND t.guild_id = tc.guild_id
        WHERE t.guild_id = %s AND t.`trigger` LIKE %s
        AND (tc.channel_id = %s)
    """
    params = (guild_id, trigger, channel_id)
    result = await execute_query(query, params)
    result = result[0] if result and result[0] else None
    if not result:
        return None
    trigger_message = TriggerMessageModel.from_row(result)
    if trigger_message.case_sensitive:
        if trigger != trigger_message.trigger:
            return None
    else:
        if trigger.lower() != trigger_message.trigger.lower():
            return None
    return trigger_message


async def create_ticket_message(
    guild_id: str,
    channel_id: str,
    introduction: str,
    ping_role: str,
    name: str,
    description: str,
    summary_channel_id: str,
) -> int | None:
    query = "INSERT INTO ticketMessages (guild_id, channel_id, introduction, pingRole, name, description, summaryChannelId) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    params = (
        guild_id,
        channel_id,
        introduction,
        ping_role,
        name,
        description,
        summary_channel_id,
    )
    return await execute_insert_and_get_id(query, params)


async def delete_ticket_message(guild_id: str, ticket_message_id: str) -> None:
    query = "DELETE FROM ticketMessages WHERE guild_id = %s AND id = %s"
    params = (guild_id, ticket_message_id)
    await execute_action(query, params)


async def get_ticket_messages(guild_id: str) -> list[TicketMessageModel]:
    query = "SELECT id, guild_id, channel_id, introduction, pingRole, name, description, summaryChannelId FROM ticketMessages WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[TicketMessageModel] = []
    async for row in TicketMessageModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_ticket_messages_by_id(ticket_message_id: str) -> TicketMessageModel | None:
    result = await execute_query(
        "SELECT id, guild_id, channel_id, introduction, pingRole, name, description, summaryChannelId FROM ticketMessages WHERE id = %s",
        (ticket_message_id,),
    )
    return TicketMessageModel.from_row(result[0]) if result else None


async def open_ticket(guild_id: str, opener_id: str, ticket_message_id: str, channel_id: str) -> None:
    query = "INSERT INTO tickets (guild_id, openerId, ticketMessageId, channel_id) VALUES (%s, %s, %s, %s)"
    params = (guild_id, opener_id, ticket_message_id, channel_id)
    await execute_action(query, params)


async def close_ticket(guild_id: str, ticket_id: str) -> None:
    query = "UPDATE tickets SET closed = 1, closedAt = NOW(), closedBy = %s WHERE guild_id = %s AND id = %s"
    params = (guild_id, ticket_id)
    await execute_action(query, params)


async def get_tickets(guild_id: str) -> list[TicketModel]:
    query = """
        SELECT guild_id, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channel_id, ticketMessageId
        FROM tickets WHERE guild_id = %s
    """
    params = (guild_id,)
    rows: list[TicketModel] = []
    async for row in TicketModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def get_ticket_by_id(guild_id: str, ticket_id: str, channel_id: str) -> TicketModel | None:
    query = """
        SELECT guild_id, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channel_id, ticketMessageId
        FROM tickets
        WHERE guild_id = %s AND ticketMessageId = %s AND channel_id = %s
    """
    params = (guild_id, ticket_id, channel_id)
    result = await execute_query(query, params)
    return TicketModel.from_row(result[0]) if result else None


async def get_ticket_by_channel_id(guild_id: str, channel_id: str) -> TicketModel | None:
    query = """
        SELECT guild_id, openerId,
               UNIX_TIMESTAMP(openedAt) as openedAt,
               closed,
               UNIX_TIMESTAMP(closedAt) as closedAt,
               closedBy, channel_id, ticketMessageId
        FROM tickets
        WHERE guild_id = %s AND channel_id = %s
    """
    params = (guild_id, channel_id)
    result = await execute_query(query, params)
    return TicketModel.from_row(result[0]) if result else None


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


async def get_twitch_online_notification(channel_id: str) -> list[TwitchOnlineNotificationModel]:
    query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE channel_id = %s"
    params = (channel_id,)
    rows: list[TwitchOnlineNotificationModel] = []
    async for row in TwitchOnlineNotificationModel.iter_rows(query, params):
        rows.append(row)
    return rows


async def set_twitch_online_notification(
    guild_id: str,
    channel_id: str,
    twitch_uuid: str,
    twitch_name: str,
    notification_message: str,
) -> None:
    print("adding twitch online notification")
    query = "INSERT INTO twitchOnlineNotification (guild_id, channel_id, twitchUuid, twitchName, notification_message) VALUES (%s, %s, %s, %s, %s)"
    params = (guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
    await execute_action(query, params)
    print("added twitch online notification")


async def remove_twitch_online_notification(id: str) -> None:
    query = "DELETE FROM twitchOnlineNotification WHERE id = %s"
    params = (id,)
    await execute_action(query, params)


async def get_twitch_online_notification_by_twitch_uuid(twitch_uuid: str) -> TwitchOnlineNotificationModel | None:
    query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE twitchUuid = %s"
    params = (twitch_uuid,)
    result = await safe_execute_query(query, params)
    return TwitchOnlineNotificationModel.from_row(result[0]) if result else None


async def get_all_twitch_notification_uuids() -> list[str]:
    query = "SELECT twitchUuid FROM twitchOnlineNotification"
    uuids: list[str] = []
    async for row in execute_query_iter(query):
        uuids.append(row[0])
    return uuids


async def get_twitch_notification_by_guild_id(guild_id: str) -> list[TwitchOnlineNotificationModel]:
    query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE guild_id = %s"
    params = (guild_id,)
    rows: list[TwitchOnlineNotificationModel] = []
    async for row in TwitchOnlineNotificationModel.iter_rows(query, params):
        rows.append(row)
    return rows


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
