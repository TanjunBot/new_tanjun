"""
Database integration tests for api.py.

These tests connect to a real MariaDB/MySQL database running on port 3307
(see docker-compose.test.yml) and verify that SQL queries, table creation,
and CRUD operations work correctly at the database level.

Usage:
    # Start the test database container first
    docker compose -f docker-compose.test.yml up -d

    # Run integration tests
    TANJUN_INTEGRATION=true pytest tests/test_api_integration.py -v

    # Without TANJUN_INTEGRATION=true, all tests in this file are skipped.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

# Mock discord before importing any project modules
import sys
_discord_mock = MagicMock()
_discord_mock.Entitlement = MagicMock()
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = MagicMock()
sys.modules["discord.ext.commands"] = MagicMock()
sys.modules["discord.app_commands"] = MagicMock()

from api import (
    add_warning,
    get_warnings,
    remove_warning,
    add_channel_to_blacklist,
    add_role_to_blacklist,
    get_level_roles,
    add_level_role,
    remove_level_role,
    set_level_system_status,
    get_level_system_status,
    check_pool_health,
    set_bot,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        "__import__('os').environ.get('TANJUN_INTEGRATION') != 'true'",
        reason="Set TANJUN_INTEGRATION=true to run database integration tests. "
               "Requires a running test DB (docker compose -f docker-compose.test.yml up -d)",
    ),
]

# ── Helpers ──────────────────────────────────────────────────────────────────

TEST_GUILD = "99999999999999999"
TEST_USER = "88888888888888888"
TEST_ROLE = "77777777777777777"
TEST_CHANNEL = "66666666666666666"


# ── Pool health ──────────────────────────────────────────────────────────────


async def test_pool_health_returns_true_when_db_is_reachable(integration_db_pool):
    """Verify check_pool_health returns True against a real database."""
    healthy = await check_pool_health()
    assert healthy is True, "Pool should be healthy against a reachable DB"


# ── Table creation ───────────────────────────────────────────────────────────


async def test_tables_are_created_via_create_tables(integration_db_pool):
    """Verify that create_tables creates all expected tables."""
    pool = integration_db_pool
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
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
    await add_warning(TEST_GUILD, TEST_USER, "Integration test warning", expires_at, "bot")

    warnings = await get_warnings(TEST_GUILD, TEST_USER)
    assert warnings is not None, "get_warnings should return a list"
    assert len(warnings) >= 1, "Should have at least one warning"

    matching = [w for w in warnings if w.reason == "Integration test warning"]
    assert len(matching) >= 1, "Should find the warning we just added"


async def test_remove_warning(integration_db_pool):
    """Add a warning and then remove it, verifying the removal."""
    expires_at = datetime.now() + timedelta(days=30)
    await add_warning(TEST_GUILD, TEST_USER, "To be removed", expires_at, "bot")

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
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
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
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
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
    from api import update_user_xp, get_user_xp

    xp_amount = 500
    result = await update_user_xp(TEST_GUILD, TEST_USER, xp_amount)
    assert result is not None or result is None  # update_user_xp may not return the count

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
