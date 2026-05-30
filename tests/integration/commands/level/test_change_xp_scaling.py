from unittest.mock import AsyncMock, patch

import pytest

from commands.level.change_xp_scaling import change_xp_scaling_command, show_xp_scalings

pytestmark = pytest.mark.asyncio


async def test_change_scaling_missing_permission(restricted_command_info):
    await change_xp_scaling_command(restricted_command_info, "medium", None)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.change_xp_scaling.set_xp_scaling", new_callable=AsyncMock)
async def test_change_scaling_success(mock_set, admin_command_info):
    await change_xp_scaling_command(admin_command_info, "medium", None)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.change_xp_scaling.set_xp_scaling", new_callable=AsyncMock)
async def test_change_scaling_custom_formula(mock_set, admin_command_info):
    await change_xp_scaling_command(admin_command_info, "custom", "level * 100")
    mock_set.assert_awaited_once()


@patch("commands.level.change_xp_scaling.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.change_xp_scaling.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_show_scalings(mock_xp, mock_formula, admin_command_info):
    await show_xp_scalings(admin_command_info, 1, 5)
    admin_command_info.reply.assert_awaited_once()


async def test_change_scaling_invalid(restricted_command_info):
    await change_xp_scaling_command(restricted_command_info, "invalid", None)
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.change_xp_scaling.set_xp_scaling", new_callable=AsyncMock)
async def test_change_scaling_hard(mock_set, admin_command_info):
    await change_xp_scaling_command(admin_command_info, "hard", None)
    mock_set.assert_awaited_once()
