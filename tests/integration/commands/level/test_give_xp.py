from unittest.mock import AsyncMock, patch

import pytest

from commands.level.give_xp import give_xp_command
from tests.helpers.discord import make_target_member

pytestmark = pytest.mark.asyncio


async def test_give_xp_command_missing_permission(restricted_command_info):
    user = make_target_member()
    await give_xp_command(restricted_command_info, user, 100)
    restricted_command_info.reply.assert_awaited_once()


async def test_give_xp_command_invalid_amount(admin_command_info):
    user = make_target_member()
    await give_xp_command(admin_command_info, user, 0)
    admin_command_info.reply.assert_awaited_once()
    assert "embed" in admin_command_info.reply.await_args.kwargs


async def test_give_xp_command_negative_amount(admin_command_info):
    user = make_target_member()
    await give_xp_command(admin_command_info, user, -5)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.give_xp.get_user_xp", new_callable=AsyncMock, return_value=100)
@patch("commands.level.give_xp.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.give_xp.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.give_xp.update_user_xp", new_callable=AsyncMock)
@patch("commands.level.give_xp.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
async def test_give_xp_command_success(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
    user = make_target_member()
    await give_xp_command(admin_command_info, user, 50)
    mock_update.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.give_xp.get_user_xp", new_callable=AsyncMock, return_value=None)
@patch("commands.level.give_xp.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.give_xp.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.give_xp.update_user_xp", new_callable=AsyncMock)
@patch("commands.level.give_xp.get_level_for_xp_async", new_callable=AsyncMock, return_value=0)
async def test_give_xp_command_new_user(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
    user = make_target_member()
    await give_xp_command(admin_command_info, user, 10)
    mock_update.assert_awaited_once()


@patch("commands.level.give_xp.get_user_xp", new_callable=AsyncMock, return_value=500)
@patch("commands.level.give_xp.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.give_xp.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.give_xp.update_user_xp", new_callable=AsyncMock)
@patch("commands.level.give_xp.get_level_for_xp_async", new_callable=AsyncMock, side_effect=[5, 6])
async def test_give_xp_command_level_change(mock_level, mock_update, mock_formula, mock_scaling, mock_xp, admin_command_info):
    user = make_target_member()
    await give_xp_command(admin_command_info, user, 200)
    admin_command_info.reply.assert_awaited_once()


async def test_give_xp_command_requires_guild(admin_command_info):
    admin_command_info.guild = None
    user = make_target_member()
    with pytest.raises(ValueError):
        await give_xp_command(admin_command_info, user, 10)
