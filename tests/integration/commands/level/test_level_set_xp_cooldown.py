import pytest
from unittest.mock import AsyncMock, patch

from commands.level.level_set_xp_cooldown import set_text_cooldown_command, set_voice_cooldown_command


pytestmark = pytest.mark.asyncio


async def test_text_cooldown_missing_permission(restricted_command_info):
    await set_text_cooldown_command(restricted_command_info, 60)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_text_cooldown", new_callable=AsyncMock)
async def test_text_cooldown_success(mock_set, admin_command_info):
    await set_text_cooldown_command(admin_command_info, 60)
    mock_set.assert_awaited_once()


async def test_text_cooldown_invalid(admin_command_info):
    await set_text_cooldown_command(admin_command_info, -1)
    admin_command_info.reply.assert_awaited_once()


async def test_voice_cooldown_missing_permission(restricted_command_info):
    await set_voice_cooldown_command(restricted_command_info, 30)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_voice_cooldown", new_callable=AsyncMock)
async def test_voice_cooldown_success(mock_set, admin_command_info):
    await set_voice_cooldown_command(admin_command_info, 30)
    mock_set.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_text_cooldown", new_callable=AsyncMock)
async def test_text_cooldown_zero(mock_set, admin_command_info):
    await set_text_cooldown_command(admin_command_info, 0)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()
