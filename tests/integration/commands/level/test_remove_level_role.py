from unittest.mock import AsyncMock, patch

import pytest

from commands.level.remove_level_role import remove_level_role_command
from tests.helpers.discord import make_role

pytestmark = pytest.mark.asyncio


async def test_remove_level_role_missing_permission(restricted_command_info):
    role = make_role()
    await remove_level_role_command(restricted_command_info, role)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.remove_level_role.get_level_role", new_callable=AsyncMock, return_value=None)
async def test_remove_level_role_not_found(mock_get, admin_command_info):
    role = make_role()
    await remove_level_role_command(admin_command_info, role)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.remove_level_role.remove_level_role", new_callable=AsyncMock)
@patch("commands.level.remove_level_role.get_level_role", new_callable=AsyncMock, return_value=True)
async def test_remove_level_role_success(mock_get, mock_remove, admin_command_info):
    role = make_role()
    await remove_level_role_command(admin_command_info, role)
    mock_remove.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.remove_level_role.remove_level_role", new_callable=AsyncMock)
@patch("commands.level.remove_level_role.get_level_role", new_callable=AsyncMock, return_value=True)
async def test_remove_level_role_guild_id(mock_get, mock_remove, admin_command_info):
    role = make_role()
    await remove_level_role_command(admin_command_info, role)
    mock_remove.assert_awaited_once_with(str(admin_command_info.guild.id), str(role.id))


async def test_remove_level_role_requires_guild(admin_command_info):
    admin_command_info.guild = None
    role = make_role()
    with pytest.raises(AssertionError):
        await remove_level_role_command(admin_command_info, role)
