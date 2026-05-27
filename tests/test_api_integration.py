"""Database integration tests for api.py.

Requires a running MariaDB/MySQL test database at 127.0.0.1:3307.
Run with Docker:
    docker compose -f compose.test.yaml up -d
    pytest tests/test_api_integration.py -v
    docker compose -f compose.test.yaml down

Skips automatically if database is unreachable or SKIP_INTEGRATION_TESTS=1.
"""

import os

import pytest

# These must be set before importing api — the conftest.py patches discord
# globally, so we need to ensure our mock is compatible.
import sys
from unittest.mock import MagicMock

# Re-patch discord after conftest to ensure Entitlement exists for api imports
_discord_mock = MagicMock()
_discord_mock.Entitlement = MagicMock()
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()

import api

# Test DB connection settings — override via env when using custom setup
TEST_DB_HOST = os.environ.get("TEST_DB_HOST", "127.0.0.1")
TEST_DB_PORT = int(os.environ.get("TEST_DB_PORT", "3307"))
TEST_DB_USER = os.environ.get("TEST_DB_USER", "root")
TEST_DB_PASSWORD = os.environ.get("TEST_DB_PASSWORD", "test")
TEST_DB_NAME = os.environ.get("TEST_DB_NAME", "tanjun_test")


pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION_TESTS", "0") == "1",
        reason="Integration tests disabled via SKIP_INTEGRATION_TESTS=1",
    ),
]


_created_tables = False


@pytest.fixture(scope="session")
async def integration_pool():
    """Create a real database connection pool for integration tests."""
    global _created_tables
    try:
        import asyncmy

        pool = await asyncmy.create_pool(
            host=TEST_DB_HOST,
            port=TEST_DB_PORT,
            user=TEST_DB_USER,
            password=TEST_DB_PASSWORD,
            db=TEST_DB_NAME,
            minsize=1,
            maxsize=2,
            autocommit=False,
        )
    except Exception as exc:
        pytest.skip(f"Test database not available at {TEST_DB_HOST}:{TEST_DB_PORT}: {exc}")
        return

    # Create tables once per session
    if not _created_tables:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    for table_name, ddl in _get_table_definitions().items():
                        await cursor.execute(ddl)
                await conn.commit()
            _created_tables = True
        except Exception as exc:
            pool.close()
            await pool.wait_closed()
            pytest.skip(f"Failed to initialize test database tables: {exc}")
            return

    yield pool

    # Session cleanup: drop all created tables
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT CONCAT('DROP TABLE IF EXISTS `', table_name, '`') "
                    "FROM information_schema.tables "
                    "WHERE table_schema = %s",
                    (TEST_DB_NAME,),
                )
                for (stmt,) in await cursor.fetchall():
                    await cursor.execute(stmt)
                await conn.commit()
    except Exception:
        pass

    pool.close()
    await pool.wait_closed()


@pytest.fixture
def bot_with_integration_pool(integration_pool, monkeypatch):
    """Patch the global _bot in api.py so execute_query uses the test pool."""

    class FakeBot:
        _pool = integration_pool

    api.set_bot(FakeBot())
    return FakeBot()


def _get_table_definitions():
    """Return the subset of DDL needed for our integration tests."""
    # Use the real create_tables logic by reading the DDL dict from api
    return {
        "warnings": (
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
        ),
        "warn_config": (
            "CREATE TABLE IF NOT EXISTS `warn_config` ("
            "  `guild_id` VARCHAR(20) PRIMARY KEY,"
            "  `expiration_days` INT DEFAULT 0,"
            "  `timeout_threshold` INT DEFAULT 0,"
            "  `timeout_duration` INT DEFAULT 0,"
            "  `kick_threshold` INT DEFAULT 0,"
            "  `ban_threshold` INT DEFAULT 0"
            ") ENGINE=InnoDB"
        ),
        "channel_overwrites": (
            "CREATE TABLE IF NOT EXISTS `channel_overwrites` ("
            "  `id` INT AUTO_INCREMENT PRIMARY KEY,"
            "  `channel_id` VARCHAR(20) NOT NULL,"
            "  `role_id` VARCHAR(20) NOT NULL,"
            "  `overwrites` JSON,"
            "  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ") ENGINE=InnoDB"
        ),
        "message_tracking_opt_out": (
            "CREATE TABLE IF NOT EXISTS `message_tracking_opt_out` ("
            "  `user_id` VARCHAR(20) PRIMARY KEY"
            ") ENGINE=InnoDB"
        ),
        "counting": (
            "CREATE TABLE IF NOT EXISTS `counting` ("
            "  `channel_id` VARCHAR(20) PRIMARY KEY,"
            "  `progress` INT UNSIGNED DEFAULT 0,"
            "  `last_counter_id` VARCHAR(20) DEFAULT NULL,"
            "  `guild_id` VARCHAR(20)"
            ") ENGINE=InnoDB"
        ),
        "level": (
            "CREATE TABLE IF NOT EXISTS `level` ("
            "  `user_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `xp` INT UNSIGNED DEFAULT 0,"
            "  `customBackground` VARCHAR(255) DEFAULT NULL,"
            "  `last_xp_gain` DATETIME DEFAULT NOW(),"
            "  `last_voice_xp_gain` DATETIME DEFAULT NOW(),"
            "  PRIMARY KEY(`user_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "blacklistedUser": (
            "CREATE TABLE IF NOT EXISTS `blacklistedUser` ("
            "  `user_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `reason` VARCHAR(255) DEFAULT NULL,"
            "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`user_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "blacklistedRole": (
            "CREATE TABLE IF NOT EXISTS `blacklistedRole` ("
            "  `role_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `reason` VARCHAR(255) DEFAULT NULL,"
            "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`role_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "blacklistedChannel": (
            "CREATE TABLE IF NOT EXISTS `blacklistedChannel` ("
            "  `channel_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `reason` VARCHAR(255) DEFAULT NULL,"
            "  `blacklisted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`channel_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "userXpBoost": (
            "CREATE TABLE IF NOT EXISTS `userXpBoost` ("
            "  `user_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
            "  `additive` TINYINT(1) DEFAULT 0,"
            "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`user_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "roleXpBoost": (
            "CREATE TABLE IF NOT EXISTS `roleXpBoost` ("
            "  `role_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
            "  `additive` TINYINT(1) DEFAULT 0,"
            "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`role_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "channelXpBoost": (
            "CREATE TABLE IF NOT EXISTS `channelXpBoost` ("
            "  `channel_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `boost` DECIMAL(4, 2) UNSIGNED DEFAULT 1,"
            "  `additive` TINYINT(1) DEFAULT 0,"
            "  `boosted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "  PRIMARY KEY(`channel_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "levelRole": (
            "CREATE TABLE IF NOT EXISTS `levelRole` ("
            "  `role_id` VARCHAR(20) NOT NULL,"
            "  `guild_id` VARCHAR(20) NOT NULL,"
            "  `level` INT UNSIGNED DEFAULT 0,"
            "  PRIMARY KEY(`role_id`, `guild_id`)"
            ") ENGINE=InnoDB"
        ),
        "levelConfig": (
            "CREATE TABLE IF NOT EXISTS `levelConfig` ("
            "  `guild_id` VARCHAR(20) PRIMARY KEY,"
            "  `difficulty` ENUM('easy', 'medium', 'hard', 'extreme', 'custom') DEFAULT 'medium',"
            "  `customFormula` VARCHAR(255) DEFAULT NULL,"
            "  `levelUpMessageActive` TINYINT(1) DEFAULT 1,"
            "  `levelUpMessage` VARCHAR(1000) DEFAULT NULL,"
            "  `levelUpChannelId` VARCHAR(20) DEFAULT NULL,"
            "  `active` TINYINT(1) DEFAULT 1,"
            "  `textCooldown` INT DEFAULT 60,"
            "  `voiceCooldown` INT DEFAULT 60"
            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci"
        ),
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestWarningCRUD:
    """Integration tests for warning CRUD operations."""

    async def test_add_and_get_warnings(self, bot_with_integration_pool):
        """Add a warning and verify it can be retrieved."""
        guild_id = "100001"
        user_id = "200001"
        reason = "Test warning"
        created_by = "999999"

        warning_id = await api.add_warning(guild_id, user_id, reason, created_by)
        assert warning_id is not None, "add_warning should return a warning ID"
        assert isinstance(warning_id, int), "warning ID should be an integer"

        warnings = await api.get_warnings(guild_id, user_id)
        assert len(warnings) == 1, f"Expected 1 warning, got {len(warnings)}"
        assert warnings[0].reason == reason
        assert warnings[0].user_id == user_id
        assert warnings[0].created_by == created_by

    async def test_add_and_remove_warning(self, bot_with_integration_pool):
        """Add a warning then remove it."""
        guild_id = "100001"
        user_id = "200002"

        warning_id = await api.add_warning(guild_id, user_id, "Remove me", "999999")
        assert warning_id is not None

        await api.remove_warning(warning_id)

        warnings = await api.get_warnings(guild_id, user_id)
        assert len(warnings) == 0, "Warning should have been removed"

    async def test_get_warnings_empty(self, bot_with_integration_pool):
        """Getting warnings for a user with none should return an empty list."""
        warnings = await api.get_warnings("999999", "888888")
        assert warnings == [], f"Expected empty list, got {warnings}"


class TestLevelCRUD:
    """Integration tests for level XP CRUD operations."""

    async def test_update_and_get_user_xp(self, bot_with_integration_pool):
        """Update XP for a user using low-level execute_action."""
        guild_id = "100001"
        user_id = "200003"

        await api.execute_action(
            "INSERT INTO level (user_id, guild_id, xp) VALUES (%s, %s, %s) "
            "ON DUPLICATE KEY UPDATE xp = xp + %s",
            (user_id, guild_id, 50, 50),
        )

        result = await api.execute_query(
            "SELECT xp FROM level WHERE user_id = %s AND guild_id = %s",
            (user_id, guild_id),
        )
        assert result is not None
        assert len(result) == 1
        assert result[0][0] == 50

    async def test_bulk_update_user_xp(self, bot_with_integration_pool):
        """Bulk update XP for multiple users."""
        guild_id = "100002"
        updates = [
            ("300001", 100),
            ("300002", 200),
            ("300003", 300),
        ]

        await api.bulk_update_user_xp(guild_id, updates)

        for user_id, expected_xp in updates:
            result = await api.execute_query(
                "SELECT xp FROM level WHERE user_id = %s AND guild_id = %s",
                (user_id, guild_id),
            )
            assert result is not None
            assert len(result) == 1
            assert result[0][0] == expected_xp, (
                f"Expected {expected_xp} XP for user {user_id}, got {result[0][0]}"
            )

    async def test_bulk_update_user_xp_handles_empty(self, bot_with_integration_pool):
        """Bulk update with empty list should not raise."""
        await api.bulk_update_user_xp("100002", [])


class TestBlacklistCRUD:
    """Integration tests for blacklist CRUD operations."""

    async def test_add_and_check_blacklisted_user(self, bot_with_integration_pool):
        """Add a user to the blacklist and verify via get_blacklist."""
        guild_id = "100001"
        user_id = "400001"

        await api.add_user_to_blacklist(guild_id, user_id, reason="spam")
        blacklist = await api.get_blacklist(guild_id)

        assert user_id in blacklist.get("users", {}), (
            f"User {user_id} should be in the blacklist"
        )
        assert blacklist["users"][user_id] == "spam"

    async def test_add_and_check_blacklisted_channel(self, bot_with_integration_pool):
        """Add a channel to the blacklist and verify."""
        guild_id = "100001"
        channel_id = "500001"

        await api.add_channel_to_blacklist(guild_id, channel_id, reason="testing")
        blacklist = await api.get_blacklist(guild_id)

        assert channel_id in blacklist.get("channels", {}), (
            f"Channel {channel_id} should be in the blacklist"
        )


class TestOptOutCRUD:
    """Integration tests for message tracking opt-out."""

    async def test_opt_out_and_check(self, bot_with_integration_pool):
        """Opt out a user and verify."""
        user_id = "600001"

        await api.opt_out(user_id)
        result = await api.check_if_opted_out(int(user_id))
        assert result is True, "User should be opted out"

    async def test_opt_in_after_opt_out(self, bot_with_integration_pool):
        """Opt in a user after opting out."""
        user_id = "600002"

        await api.opt_out(user_id)
        await api.opt_in(user_id)
        result = await api.check_if_opted_out(int(user_id))
        assert result is False, "User should not be opted out after opting in"


class TestXPBoostsCRUD:
    """Integration tests for XP boost CRUD operations."""

    async def test_add_and_get_user_boost(self, bot_with_integration_pool):
        """Add a user XP boost and verify retrieval."""
        guild_id = "100001"
        user_id = "700001"

        await api.add_user_boost(guild_id, user_id, boost=1.5, additive=False)
        boost = await api.get_user_boost(guild_id, user_id)

        assert boost is not None
        assert float(boost.boost) == pytest.approx(1.5, rel=1e-2)

    async def test_add_and_get_role_boost(self, bot_with_integration_pool):
        """Add a role XP boost and verify retrieval."""
        guild_id = "100001"
        role_id = "800001"

        await api.add_role_boost(guild_id, role_id, boost=2.0, additive=False)

        result = await api.execute_query(
            "SELECT boost FROM roleXpBoost WHERE role_id = %s AND guild_id = %s",
            (role_id, guild_id),
        )
        assert result is not None
        assert len(result) == 1
        assert float(result[0][0]) == pytest.approx(2.0, rel=1e-2)

    async def test_get_user_boost_missing(self, bot_with_integration_pool):
        """Getting a boost for a non-existent user should return None."""
        boost = await api.get_user_boost("999999", "000000")
        assert boost is None


class TestLevelConfigCRUD:
    """Integration tests for level configuration."""

    async def test_set_and_get_xp_scaling(self, bot_with_integration_pool):
        """Set XP scaling and verify retrieval."""
        guild_id = "100001"

        await api.set_xp_scaling(guild_id, difficulty="hard")
        scaling = await api.get_xp_scaling(guild_id)

        assert scaling is not None
        assert scaling == "hard", f"Expected 'hard' scaling, got {scaling}"

    async def test_set_custom_formula_changes_scaling(self, bot_with_integration_pool):
        """Setting a custom formula should change scaling to 'custom'."""
        guild_id = "100002"

        await api.set_custom_formula(guild_id, "x**2 + 100")
        scaling = await api.get_xp_scaling(guild_id)

        assert scaling is not None
        assert scaling == "custom", f"Expected 'custom' scaling, got {scaling}"

    async def test_get_xp_scaling_default(self, bot_with_integration_pool):
        """Getting XP scaling for a guild with no config should return 'medium'."""
        scaling = await api.get_xp_scaling("__nonexistent__")
        assert scaling == "medium", f"Expected default 'medium', got {scaling}"


class TestChannelOverwritesCRUD:
    """Integration tests for channel overwrites."""

    async def test_save_and_get_channel_overwrites(self, bot_with_integration_pool):
        """Save channel overwrites and retrieve them."""
        channel_id = "900001"
        role_id = "900002"
        overwrites = {"view": True, "send": False}

        ow_id = await api.save_channel_overwrites(channel_id, role_id, overwrites)
        assert ow_id is not None
        assert isinstance(ow_id, int)

        loaded = await api.get_channel_overwrites(channel_id)
        assert len(loaded) == 1
        assert loaded[0].role_id == role_id

    async def test_clear_channel_overwrites(self, bot_with_integration_pool):
        """Clear all overwrites for a channel."""
        channel_id = "900003"

        await api.save_channel_overwrites(channel_id, "950001", {"view": True})
        await api.clear_channel_overwrites(channel_id)

        loaded = await api.get_channel_overwrites(channel_id)
        assert len(loaded) == 0, "Overwrites should be cleared"


class TestCountingCRUD:
    """Integration tests for counting minigame."""

    async def test_counting_insert_and_read(self, bot_with_integration_pool):
        """Insert counting config and read it back."""
        channel_id = "counting_test_1"
        guild_id = "100001"

        await api.execute_action(
            "INSERT INTO counting (channel_id, progress, last_counter_id, guild_id) "
            "VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE progress = progress",
            (channel_id, 42, "user_1", guild_id),
        )

        result = await api.execute_query(
            "SELECT progress FROM counting WHERE channel_id = %s",
            (channel_id,),
        )
        assert result is not None
        assert result[0][0] == 42


class TestWarnConfigCRUD:
    """Integration tests for warn configuration."""

    async def test_set_and_get_warn_config(self, bot_with_integration_pool):
        """Set warn config and retrieve it."""
        guild_id = "100001"

        await api.set_warn_config(
            guild_id,
            expiration_days=30,
            timeout_threshold=3,
            timeout_duration=60,
            kick_threshold=5,
            ban_threshold=10,
        )

        config = await api.get_warn_config(guild_id)
        assert config is not None
        assert config.expiration_days == 30
        assert config.timeout_threshold == 3
        assert config.kick_threshold == 5
        assert config.ban_threshold == 10


class TestLevelRoleCRUD:
    """Integration tests for level role assignments."""

    async def test_add_and_get_level_roles(self, bot_with_integration_pool):
        """Add level roles and retrieve them."""
        guild_id = "100001"

        await api.add_level_role(role_id="role_10", guild_id=guild_id, level=10)
        await api.add_level_role(role_id="role_20", guild_id=guild_id, level=20)

        roles = await api.get_level_roles(guild_id)
        assert len(roles) >= 2

        found_levels = {r.level for r in roles}
        assert 10 in found_levels
        assert 20 in found_levels

    async def test_remove_level_role(self, bot_with_integration_pool):
        """Remove a level role and verify it's gone."""
        guild_id = "100001"
        role_id = "role_remove_1"

        await api.add_level_role(role_id=role_id, guild_id=guild_id, level=15)
        await api.remove_level_role(role_id=role_id, guild_id=guild_id)

        roles = await api.get_level_roles(guild_id)
        assert not any(r.role_id == role_id for r in roles), (
            f"Role {role_id} should have been removed"
        )


class TestSafeExecuteQuery:
    """Integration tests for safe_execute_query."""

    async def test_safe_execute_query_returns_list(self, bot_with_integration_pool):
        """safe_execute_query should return a list even on empty results."""
        result = await api.safe_execute_query(
            "SELECT * FROM level WHERE guild_id = %s",
            ("nonexistent_guild_12345",),
        )
        assert isinstance(result, list)

    async def test_safe_execute_query_on_nonexistent_table(self, bot_with_integration_pool):
        """safe_execute_query should return empty list on error (e.g. non-existent table)."""
        result = await api.safe_execute_query("SELECT * FROM nonexistent_table_xyz")
        assert isinstance(result, list)
        assert result == []


class TestHealthCheck:
    """Integration tests for pool health check."""

    async def test_check_pool_health(self, bot_with_integration_pool):
        """check_pool_health should return True with a working pool."""
        healthy = await api.check_pool_health()
        assert healthy is True

    async def test_check_pool_health_no_pool(self):
        """check_pool_health should return False when no pool is available."""
        api.set_bot(None)
        healthy = await api.check_pool_health()
        assert healthy is False
