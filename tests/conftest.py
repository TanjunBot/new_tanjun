"""Pytest configuration and fixtures for Tanjun bot tests."""

import sys
from unittest.mock import MagicMock

import pytest

import tests.mock_config as mock_config

# Apply mock config before any test imports
mock_config.patch_config_module()

# Create a proper mock for discord that allows utility.py to import successfully
_discord_mock = MagicMock()
_discord_mock.User = MagicMock()
_discord_mock.Message = MagicMock()
_discord_mock.Embed = MagicMock()
_discord_mock.AllowedMentions = MagicMock()
_discord_mock.File = MagicMock()
_discord_mock.Forbidden = Exception
_discord_mock.HTTPException = Exception
_discord_mock.abc = MagicMock()
_discord_mock.abc.Messageable = MagicMock()
_discord_mock.ext = MagicMock()
_discord_mock.ext.commands = MagicMock()
_discord_mock.ext.commands.Cog = type("Cog", (), {})
_discord_mock.ext.commands.Context = MagicMock()
_discord_mock.ext.commands.Bot = MagicMock()
_discord_mock.ext.commands.AutoShardedBot = MagicMock()
_discord_mock.ext.commands.command = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.hybrid_command = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.is_owner = lambda f: f
_discord_mock.ext.commands.cooldown = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.Command = type("Command", (), {})
_discord_mock.app_commands = MagicMock()
_discord_mock.app_commands.Command = type("AppCommand", (), {})
_discord_mock.app_commands.Group = type("Group", (), {})
_discord_mock.app_commands.locale_str = lambda s: s
_discord_mock.app_commands.describe = lambda **kw: lambda f: f
_discord_mock.app_commands.choices = lambda *a, **kw: lambda f: f
_discord_mock.app_commands.Range = lambda *a, **kw: int
_discord_mock.app_commands.Choice = lambda **kw: type("Choice", (), kw)
_discord_mock.Interaction = MagicMock()
_discord_mock.Member = MagicMock()
_discord_mock.VoiceState = MagicMock()
_discord_mock.Guild = MagicMock()
_discord_mock.CategoryChannel = MagicMock()
_discord_mock.VoiceChannel = MagicMock()
_discord_mock.StageChannel = MagicMock()
_discord_mock.TextChannel = MagicMock()
_discord_mock.Thread = MagicMock()
_discord_mock.Embed = MagicMock
_discord_mock.Colour = MagicMock()
_discord_mock.Color = MagicMock()
_discord_mock.Attachment = MagicMock()
_discord_mock.Object = MagicMock()
_discord_mock.PartialMessageable = MagicMock()

# Store original discord for tests that need it
_original_discord = sys.modules.get("discord", None)
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = _discord_mock.ext
sys.modules["discord.ext.commands"] = _discord_mock.ext.commands


@pytest.fixture
def mock_db_pool() -> MagicMock:
    """Create a mock database connection pool."""
    pool = MagicMock()
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__aenter__.return_value = cursor
    pool.acquire.return_value.__aenter__.return_value = conn
    return pool


@pytest.fixture
def mock_bot(mock_db_pool: MagicMock) -> MagicMock:
    """Create a mock bot instance with a database pool."""
    bot = MagicMock()
    bot._pool = mock_db_pool
    return bot


# --- Integration test fixtures (requires test database container) ---

@pytest.fixture(scope="session")
def integration_mode() -> str:
    """
    Return the integration test mode.

    Set TANJUN_INTEGRATION=true in environment to enable real database tests.
    Tests default to 'skip' to avoid requiring a running test DB.
    """
    import os
    return os.environ.get("TANJUN_INTEGRATION", "false").lower()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the session-scoped integration fixtures."""
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def integration_db_pool():
    """
    Create a real database connection pool pointing at the test database.

    Requires the test database to be running (e.g. via docker-compose.test.yml):
        docker compose -f docker-compose.test.yml up -d

    Yields the pool and drops + recreates all tables on teardown so each
    test session starts with a clean schema.
    """
    import os

    import asyncmy

    host = os.environ.get("TANJUN_TEST_DB_HOST", "localhost")
    port = int(os.environ.get("TANJUN_TEST_DB_PORT", "3307"))
    user = os.environ.get("TANJUN_TEST_DB_USER", "root")
    password = os.environ.get("TANJUN_TEST_DB_PASSWORD", "test")
    db = os.environ.get("TANJUN_TEST_DB_NAME", "tanjun_test")

    pool = await asyncmy.create_pool(
        host=host,
        port=port,
        user=user,
        password=password,
        db=db,
        minsize=1,
        maxsize=2,
    )

    # Set the global pool so api._get_pool() resolves
    import api
    from api import set_bot
    _fake_bot = MagicMock()
    _fake_bot._pool = pool
    original_bot = api._bot
    set_bot(_fake_bot)

    # Create all tables
    from api import create_tables
    await create_tables(_fake_bot)

    yield pool

    # Clean up: drop all tables
    async with pool.acquire() as conn, conn.cursor() as cursor:
        await cursor.execute(
            "SELECT CONCAT('DROP TABLE IF EXISTS `', table_name, '`') "
            "FROM information_schema.tables WHERE table_schema = %s",
            (db,),
        )
        drop_queries = await cursor.fetchall()
        for (dq,) in drop_queries:
            await cursor.execute(dq)

    pool.close()
    await pool.wait_closed()

    # Restore original bot state
    set_bot(original_bot)
