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
