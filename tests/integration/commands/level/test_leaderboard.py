from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.level.leaderboard import leaderboard

pytestmark = pytest.mark.asyncio


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=0)
async def test_leaderboard_no_data(mock_count, admin_command_info):
    admin_command_info.message = MagicMock()
    admin_command_info.message.channel = admin_command_info.channel
    admin_command_info.message.channel.send = AsyncMock()
    await leaderboard(admin_command_info)
    admin_command_info.message.channel.send.assert_awaited_once()


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock)
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_with_data(
    mock_xp_level, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info
):
    entry = MagicMock()
    entry.user_id = "111111111"
    entry.xp = 500
    mock_page.return_value = [entry]
    await leaderboard(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=25)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_page_clamped(
    mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info
):
    await leaderboard(admin_command_info, page=999)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=5)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_page_zero(
    mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info
):
    await leaderboard(admin_command_info, page=0)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=3)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_single_page(
    mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info
):
    await leaderboard(admin_command_info, page=1)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("embed") is not None
