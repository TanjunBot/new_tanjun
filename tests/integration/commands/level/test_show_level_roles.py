import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.level.show_level_roles import show_level_roles_command


pytestmark = pytest.mark.asyncio


async def test_show_level_roles_missing_permission(restricted_command_info):
    await show_level_roles_command(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock, return_value=[])
async def test_show_level_roles_empty(mock_get, admin_command_info):
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock)
async def test_show_level_roles_with_data(mock_get, admin_command_info):
    group = MagicMock()
    group.level = 5
    group.role_ids = ["555555555"]
    mock_get.return_value = [group]
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock)
async def test_show_level_roles_view(mock_get, admin_command_info):
    group = MagicMock()
    group.level = 1
    group.role_ids = ["111"]
    mock_get.return_value = [group]
    await show_level_roles_command(admin_command_info)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("view") is not None


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock, return_value=[])
async def test_show_level_roles_calls_api(mock_get, admin_command_info):
    await show_level_roles_command(admin_command_info)
    mock_get.assert_awaited_once_with(str(admin_command_info.guild.id))
