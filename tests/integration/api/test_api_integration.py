"""Database integration tests for api.py.

These tests connect to a real MariaDB/MySQL database to verify that SQL queries,
table creation, and CRUD operations work correctly at the database level.

Setup and Usage:
    # Start the test database container
    docker compose -f docker-compose.test.yml up -d

    # Run integration tests
    pytest tests/test_api_integration.py -v

    # Cleanup
    docker compose -f docker-compose.test.yml down

Skips automatically if database is unreachable or SKIP_INTEGRATION_TESTS=1.
Set TANJUN_INTEGRATION=true as an alternative environment trigger.
"""

import os
from datetime import datetime, timedelta

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

import api  # noqa: E402
from api import (  # noqa: E402
    add_channel_to_blacklist,
    add_level_role,
    add_role_to_blacklist,
    add_warning,
    check_pool_health,
    get_level_roles,
    get_level_system_status,
    get_warnings,
    remove_level_role,
    remove_warning,
    set_level_system_status,
)

# Test DB connection settings — override via env when using custom setup
TEST_DB_HOST = os.environ.get("TANJUN_TEST_DB_HOST", os.environ.get("TEST_DB_HOST", "127.0.0.1"))
TEST_DB_PORT = int(os.environ.get("TANJUN_TEST_DB_PORT", os.environ.get("TEST_DB_PORT", "3307")))
TEST_DB_USER = os.environ.get("TANJUN_TEST_DB_USER", os.environ.get("TEST_DB_USER", "test_user"))
TEST_DB_PASSWORD = os.environ.get("TANJUN_TEST_DB_PASSWORD", os.environ.get("TEST_DB_PASSWORD", "test_password"))
TEST_DB_NAME = os.environ.get("TANJUN_TEST_DB_NAME", os.environ.get("TEST_DB_NAME", "tanjun_test"))

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        os.environ.get("SKIP_INTEGRATION_TESTS", "0") == "1",
        reason="Integration tests disabled via SKIP_INTEGRATION_TESTS=1",
    ),
]


# Test constants for function-based tests (from version 3)
TEST_GUILD = "99999999999999999"
TEST_USER = "88888888888888888"
TEST_ROLE = "77777777777777777"
TEST_CHANNEL = "66666666666666666"


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
        async with pool.acquire() as conn, conn.cursor() as cursor:
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
    return api.get_table_definitions()


# ---------------------------------------------------------------------------
# Class-based tests (from version 2)
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
            "INSERT INTO level (user_id, guild_id, xp) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE xp = xp + %s",
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
            assert result[0][0] == expected_xp, f"Expected {expected_xp} XP for user {user_id}, got {result[0][0]}"

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

        assert user_id in blacklist.get("users", {}), f"User {user_id} should be in the blacklist"
        assert blacklist["users"][user_id] == "spam"

    async def test_add_and_check_blacklisted_channel(self, bot_with_integration_pool):
        """Add a channel to the blacklist and verify."""
        guild_id = "100001"
        channel_id = "500001"

        await api.add_channel_to_blacklist(guild_id, channel_id, reason="testing")
        blacklist = await api.get_blacklist(guild_id)

        assert channel_id in blacklist.get("channels", {}), f"Channel {channel_id} should be in the blacklist"


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
        assert not any(r.role_id == role_id for r in roles), f"Role {role_id} should have been removed"


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


# ---------------------------------------------------------------------------
# Function-based tests (from version 3)
# These use the integration_db_pool fixture from conftest.py
# ---------------------------------------------------------------------------


async def test_pool_health_returns_true_when_db_is_reachable(integration_db_pool):
    """Verify check_pool_health returns True against a real database."""
    healthy = await check_pool_health()
    assert healthy is True, "Pool should be healthy against a reachable DB"


# ── Table creation ───────────────────────────────────────────────────────────


async def test_tables_are_created_via_create_tables(integration_db_pool):
    """Verify that create_tables creates all expected tables."""

    pool = integration_db_pool
    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute("SHOW TABLES")
        tables = {row[0] for row in await cursor.fetchall()}

    # Core expected tables
    expected = {
        "warnings",
        "warn_config",
        "level",
        "levelConfig",
        "levelRole",
        "blacklistedChannel",
        "blacklistedRole",
        "blacklistedUser",
        "userXpBoost",
        "channelXpBoost",
        "roleXpBoost",
    }
    missing = expected - tables
    assert not missing, f"Expected tables missing: {missing}"


# ── Warnings CRUD ────────────────────────────────────────────────────────────


async def test_add_and_retrieve_warning(integration_db_pool):
    """Write a warning to the database and read it back."""
    expires_at = datetime.now() + timedelta(days=30)
    await add_warning(TEST_GUILD, TEST_USER, "Integration test warning", "bot", expires_at)

    warnings = await get_warnings(TEST_GUILD, TEST_USER)
    assert warnings is not None, "get_warnings should return a list"
    assert len(warnings) >= 1, "Should have at least one warning"

    matching = [w for w in warnings if w.reason == "Integration test warning"]
    assert len(matching) >= 1, "Should find the warning we just added"


async def test_remove_warning(integration_db_pool):
    """Add a warning and then remove it, verifying the removal."""
    expires_at = datetime.now() + timedelta(days=30)
    await add_warning(TEST_GUILD, TEST_USER, "To be removed", "bot", expires_at)

    warnings_before = await get_warnings(TEST_GUILD, TEST_USER)
    target = [w for w in (warnings_before or []) if w.reason == "To be removed"]
    assert len(target) >= 1, "Should find the warning to remove"

    # Remove the first matching warning
    warning_id = target[0].id
    await remove_warning(warning_id)

    warnings_after = await get_warnings(TEST_GUILD, TEST_USER) or []
    still_around = [w for w in warnings_after if w.id == warning_id]
    assert len(still_around) == 0, "Warning should no longer be present after removal"


# ── Blacklist CRUD ───────────────────────────────────────────────────────────


async def test_channel_blacklist_round_trip(integration_db_pool):
    """Verify a channel can be blacklisted and the operation doesn't error."""

    await add_channel_to_blacklist(TEST_GUILD, TEST_CHANNEL, "Integration test channel blacklist")

    # Verify by reading directly from the database
    pool = integration_db_pool
    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT channel_id, reason FROM blacklistedChannel WHERE guild_id = %s AND channel_id = %s",
            (TEST_GUILD, TEST_CHANNEL),
        )
        row = await cursor.fetchone()
    assert row is not None, "Channel should appear in blacklist"
    assert row[0] == TEST_CHANNEL
    assert row[1] == "Integration test channel blacklist"


async def test_role_blacklist_round_trip(integration_db_pool):
    """Verify a role can be blacklisted and the operation doesn't error."""

    await add_role_to_blacklist(TEST_GUILD, TEST_ROLE, "Integration test role blacklist")

    # Verify by reading directly from the database
    pool = integration_db_pool
    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT role_id, reason FROM blacklistedRole WHERE guild_id = %s AND role_id = %s",
            (TEST_GUILD, TEST_ROLE),
        )
        row = await cursor.fetchone()
    assert row is not None, "Role should appear in blacklist"
    assert row[0] == TEST_ROLE
    assert row[1] == "Integration test role blacklist"


# ── Level system CRUD ────────────────────────────────────────────────────────


async def test_level_system_status_toggle(integration_db_pool):
    """Enable and disable the level system for a guild."""
    # Start with disabled
    await set_level_system_status(TEST_GUILD, False)
    enabled = await get_level_system_status(TEST_GUILD)
    assert enabled is False, "Level system should be disabled"

    # Enable
    await set_level_system_status(TEST_GUILD, True)
    enabled = await get_level_system_status(TEST_GUILD)
    assert enabled is True, "Level system should be enabled"


async def test_level_role_add_and_remove(integration_db_pool):
    """Add a level role, verify it's returned, then remove it."""
    await add_level_role(TEST_GUILD, TEST_ROLE, 10)

    roles = await get_level_roles(TEST_GUILD)
    matching = [r for r in (roles or []) if r.role_id == TEST_ROLE]
    assert len(matching) >= 1, "Level role should be present after adding"
    assert matching[0].level == 10

    # Remove
    await remove_level_role(TEST_GUILD, TEST_ROLE)
    roles_after = await get_level_roles(TEST_GUILD) or []
    still_around = [r for r in roles_after if r.role_id == TEST_ROLE]
    assert len(still_around) == 0, "Level role should be gone after removal"


# ── XP CRUD ──────────────────────────────────────────────────────────────────


async def test_xp_insert_and_retrieve(integration_db_pool):
    """Write XP for a user and verify it reads back correctly."""
    from api import get_user_xp, update_user_xp

    xp_amount = 500
    await update_user_xp(TEST_GUILD, TEST_USER, xp_amount)

    xp = await get_user_xp(TEST_GUILD, TEST_USER)
    assert xp is not None, "XP should be retrievable after insert"
    assert xp >= xp_amount, f"Expected at least {xp_amount} XP, got {xp}"


async def test_bulk_xp_update(integration_db_pool):
    """Bulk-update XP for multiple users and verify results."""
    from api import bulk_update_user_xp, get_user_xp

    user_a = "10000000000000001"
    user_b = "10000000000000002"
    entries = [
        (user_a, 200),
        (user_b, 300),
    ]

    await bulk_update_user_xp(TEST_GUILD, entries)

    xp_a = await get_user_xp(TEST_GUILD, user_a)
    xp_b = await get_user_xp(TEST_GUILD, user_b)
    # Since other tests may have inserted XP, we verify at-minimum values
    assert xp_a is not None and xp_a >= 200, f"user_a XP should be >= 200, got {xp_a}"
    assert xp_b is not None and xp_b >= 300, f"user_b XP should be >= 300, got {xp_b}"


# ── Token CRUD ───────────────────────────────────────────────────────────────


class TestTokenCRUD:
    async def test_include_and_get_token(self, bot_with_integration_pool):
        user_id = "token_user_1"
        await api.includeToToken(user_id)
        total = await api.getToken(user_id)
        assert total >= 500

    async def test_add_and_use_token(self, bot_with_integration_pool):
        user_id = "token_user_2"
        await api.includeToToken(user_id)
        before = await api.getToken(user_id)
        await api.useToken(user_id, 10)
        after = await api.getToken(user_id)
        assert after <= before

    async def test_get_token_overview(self, bot_with_integration_pool):
        user_id = "token_user_3"
        await api.includeToToken(user_id)
        overview = await api.getTokenOverview(user_id)
        assert overview is not None
        assert overview.freeToken >= 0


# ── Cooldown CRUD ────────────────────────────────────────────────────────────


class TestCooldownCRUD:
    async def test_text_and_voice_cooldown(self, bot_with_integration_pool):
        guild_id = "cooldown_guild_1"
        await api.set_text_cooldown(guild_id, 45)
        await api.set_voice_cooldown(guild_id, 90)
        assert await api.get_text_cooldown(guild_id) == 45
        assert await api.get_voice_cooldown(guild_id) == 90


# ── Feedback CRUD ──────────────────────────────────────────────────────────────


class TestFeedbackCRUD:
    async def test_block_and_unblock_feedback(self, bot_with_integration_pool):
        user_id = "feedback_user_1"
        await api.feedbackBlockUser(user_id)
        assert await api.feedbackIsBlocked(user_id) is True
        await api.feedbackUnblockUser(user_id)
        assert await api.feedbackIsBlocked(user_id) is False


# ── Auto publish CRUD ──────────────────────────────────────────────────────────


class TestAutoPublishCRUD:
    async def test_autopublish_round_trip(self, bot_with_integration_pool):
        channel_id = "autopublish_ch_1"
        await api.addAutoPublish(channel_id)
        assert await api.checkIfChannelIsAutopublish(channel_id) is True
        await api.removeAutoPublish(channel_id)
        assert await api.checkIfChannelIsAutopublish(channel_id) is False


# ── Media channel CRUD ─────────────────────────────────────────────────────────


class TestMediaChannelCRUD:
    async def test_media_channel(self, bot_with_integration_pool):
        guild_id = "media_guild_1"
        channel_id = "media_ch_1"
        await api.add_media_channel(guild_id, channel_id)
        assert await api.get_media_channel(channel_id) is True
        await api.remove_media_channel(guild_id, channel_id)
        assert await api.get_media_channel(channel_id) is False


# ── Trigger message CRUD ───────────────────────────────────────────────────────


class TestTriggerMessageCRUD:
    async def test_add_and_remove_trigger(self, bot_with_integration_pool):
        guild_id = "trigger_guild_1"
        await api.add_trigger_message(guild_id, "hello", "world")
        triggers = await api.get_trigger_messages(guild_id)
        assert any(t.trigger == "hello" for t in triggers)
        await api.remove_trigger_message(guild_id, "hello")
        triggers_after = await api.get_trigger_messages(guild_id)
        assert not any(t.trigger == "hello" for t in triggers_after)


# ── Wordchain CRUD ─────────────────────────────────────────────────────────────


class TestWordchainCRUD:
    async def test_wordchain_round_trip(self, bot_with_integration_pool):
        channel_id = "wordchain_ch_1"
        guild_id = "wordchain_guild_1"
        user_id = "wordchain_user_1"
        await api.set_wordchain_word(channel_id, "apple", guild_id, user_id)
        assert await api.get_wordchain_word(channel_id) == "apple"
        assert await api.get_wordchain_last_user_id(channel_id) == user_id
        await api.clear_wordchain(channel_id)
        assert await api.get_wordchain_word(channel_id) is None


# ── Dynamic slowmode CRUD ──────────────────────────────────────────────────────


class TestDynamicSlowmodeCRUD:
    async def test_dynamicslowmode(self, bot_with_integration_pool):
        guild_id = "slow_guild_1"
        channel_id = "slow_ch_1"
        await api.add_dynamicslowmode(guild_id, channel_id, 5, 10, 60)
        config = await api.get_dynamicslowmode(channel_id)
        assert config is not None
        await api.remove_dynamicslowmode(guild_id, channel_id)
        assert await api.get_dynamicslowmode(channel_id) is None


# ── Brawlstars CRUD ────────────────────────────────────────────────────────────


class TestBrawlstarsCRUD:
    async def test_link_account(self, bot_with_integration_pool):
        user_id = "brawl_user_1"
        tag = "#TESTTAG"
        await api.add_brawlstars_linked_account(user_id, tag)
        assert await api.get_brawlstars_linked_account(user_id) == tag
        await api.remove_brawlstars_linked_account(user_id)
        assert await api.get_brawlstars_linked_account(user_id) is None


# ── Level config extended ──────────────────────────────────────────────────────


class TestLevelConfigExtended:
    async def test_levelup_message_and_channel(self, bot_with_integration_pool):
        guild_id = "level_cfg_1"
        await api.set_levelup_message(guild_id, "GG {user}")
        await api.set_levelup_channel(guild_id, "chan_123")
        await api.set_levelup_message_status(guild_id, False)
        assert await api.get_levelup_message(guild_id) == "GG {user}"
        assert await api.get_levelup_channel(guild_id) == "chan_123"
        assert await api.get_levelup_message_status(guild_id) is False

    async def test_get_custom_formula(self, bot_with_integration_pool):
        guild_id = "level_cfg_2"
        await api.set_custom_formula(guild_id, "x * 3")
        assert await api.get_custom_formula(guild_id) == "x * 3"


# ── Blacklist removal ──────────────────────────────────────────────────────────


class TestBlacklistRemoval:
    async def test_remove_channel_blacklist(self, bot_with_integration_pool):
        guild_id = "bl_rem_guild_1"
        channel_id = "bl_rem_ch_1"
        await api.add_channel_to_blacklist(guild_id, channel_id, "test")
        await api.remove_channel_from_blacklist(guild_id, channel_id)
        bl = await api.get_blacklist(guild_id)
        assert not any(e.entity_id == channel_id for e in bl.get("channels", []))

    async def test_remove_role_blacklist(self, bot_with_integration_pool):
        guild_id = "bl_rem_guild_2"
        role_id = "bl_rem_role_1"
        await api.add_role_to_blacklist(guild_id, role_id, "test")
        await api.remove_role_from_blacklist(guild_id, role_id)
        bl = await api.get_blacklist(guild_id)
        assert not any(e.entity_id == role_id for e in bl.get("roles", []))


# ── XP boost removal ───────────────────────────────────────────────────────────


class TestXpBoostRemoval:
    async def test_remove_user_boost(self, bot_with_integration_pool):
        guild_id = "boost_guild_1"
        user_id = "boost_user_1"
        await api.add_user_boost(guild_id, user_id, 2.0, False)
        assert await api.get_user_boost(guild_id, user_id) is not None
        await api.remove_user_boost(guild_id, user_id)
        assert await api.get_user_boost(guild_id, user_id) is None

    async def test_channel_boost(self, bot_with_integration_pool):
        guild_id = "boost_guild_2"
        channel_id = "boost_ch_1"
        await api.add_channel_boost(guild_id, channel_id, 1.5, True)
        boost = await api.get_channel_boost(guild_id, channel_id)
        assert boost is not None
        await api.remove_channel_boost(guild_id, channel_id)
        assert await api.get_channel_boost(guild_id, channel_id) is None


# ── Parametrized guild isolation ───────────────────────────────────────────────


@pytest.mark.parametrize("guild_suffix", range(10))
async def test_level_system_status_per_guild(bot_with_integration_pool, guild_suffix: int):
    guild_id = f"param_guild_{guild_suffix}"
    await set_level_system_status(guild_id, guild_suffix % 2 == 0)
    status = await get_level_system_status(guild_id)
    assert status == (guild_suffix % 2 == 0)


@pytest.mark.parametrize("xp_value", [10, 25, 50, 75, 100, 150, 200, 250, 300, 500])
async def test_xp_values_round_trip(bot_with_integration_pool, xp_value: int):
    from api import get_user_xp, update_user_xp

    guild_id = f"xp_guild_{xp_value}"
    user_id = f"xp_user_{xp_value}"
    await update_user_xp(guild_id, user_id, xp_value)
    xp = await get_user_xp(guild_id, user_id)
    assert xp is not None and xp >= xp_value


@pytest.mark.parametrize("reason", ["spam", "harassment", "nsfw", "raid", "other"])
async def test_warning_reasons(bot_with_integration_pool, reason: str):
    guild_id = f"warn_guild_{reason}"
    user_id = f"warn_user_{reason}"
    expires = datetime.now() + timedelta(days=7)
    await add_warning(guild_id, user_id, reason, "mod", expires)
    warnings = await get_warnings(guild_id, user_id)
    assert any(w.reason == reason for w in warnings)
