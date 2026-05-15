import sys
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_config():
    """Patch config module for all tests to avoid requiring .env file."""
    from tests.mock_config import patch_config_module

    mock = patch_config_module()
    yield mock
    if "config" in sys.modules:
        del sys.modules["config"]


@pytest.fixture
def mock_bot():
    """Create a mock Discord bot with a database pool."""
    bot = MagicMock()
    pool = MagicMock()
    pool.acquire = MagicMock()
    bot._pool = pool
    bot.application_id = 1234567890
    bot.user = MagicMock()
    bot.user.id = 999999
    bot.user.name = "TestBot"
    bot.user.discriminator = "0001"
    bot._connection = MagicMock()
    bot.guilds = []
    return bot


@pytest.fixture
def mock_pool(mock_bot):
    """Return the mock pool from mock_bot."""
    return mock_bot._pool


@pytest.fixture
def mock_interaction(mock_bot):
    """Create a mock Discord interaction."""
    interaction = MagicMock()
    interaction.user = MagicMock()
    interaction.user.id = 111111
    interaction.user.name = "TestUser"
    interaction.user.mention = "<@111111>"
    interaction.user.bot = False
    interaction.user.roles = []
    interaction.guild = MagicMock()
    interaction.guild.id = 222222
    interaction.guild.preferred_locale = "en-US"
    interaction.channel = MagicMock()
    interaction.channel.id = 333333
    interaction.client = mock_bot
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.locale = "en-US"
    interaction.guild_locale = "en-US"
    return interaction