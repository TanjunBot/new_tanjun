from unittest.mock import AsyncMock, patch

import pytest

from commands.level.add_level_role import add_level_role_command
from tests.helpers.discord import make_role

pytestmark = pytest.mark.asyncio


async def test_add_level_role_command_missing_permission(restricted_command_info):
    role = make_role()
    await add_level_role_command(restricted_command_info, role, 5)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.add_level_role.add_level_role", new_callable=AsyncMock)
async def test_add_level_role_command_success(mock_api, admin_command_info):
    role = make_role()
    await add_level_role_command(admin_command_info, role, 5)
    mock_api.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.add_level_role.add_level_role", new_callable=AsyncMock)
async def test_add_level_role_command_invalid_level(mock_api, admin_command_info):
    role = make_role()
    await add_level_role_command(admin_command_info, role, 0)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.add_level_role.add_level_role", new_callable=AsyncMock)
async def test_add_level_role_command_guild_id_passed(mock_api, admin_command_info):
    role = make_role()
    await add_level_role_command(admin_command_info, role, 10)
    if mock_api.await_count:
        args = mock_api.await_args.args
        assert str(admin_command_info.guild.id) in args


async def test_add_level_role_command_requires_guild(admin_command_info):
    admin_command_info.guild = None
    role = make_role()
    with pytest.raises((AssertionError, ValueError)):
        await add_level_role_command(admin_command_info, role, 5)


@patch("commands.level.add_level_role.add_level_role", new_callable=AsyncMock)
async def test_add_level_role_command_reply_embed(mock_api, admin_command_info):
    role = make_role()
    await add_level_role_command(admin_command_info, role, 3)
    assert "embed" in admin_command_info.reply.await_args.kwargs
