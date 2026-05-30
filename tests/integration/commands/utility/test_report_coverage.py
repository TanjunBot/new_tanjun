from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.utility.report import report
from tests.helpers.discord import make_target_member


pytestmark = pytest.mark.asyncio


async def test_report_no_guild(restricted_command_info):
    restricted_command_info.guild = None
    await report(restricted_command_info, "a" * 12, make_target_member())
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=True)
async def test_report_blocked(mock_blocked, admin_command_info):
    await report(admin_command_info, "a" * 12, make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_no_channel_configured(mock_blocked, mock_channel, admin_command_info):
    await report(admin_command_info, "a" * 12, make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value="999999999")
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_channel_not_found(mock_blocked, mock_channel, admin_command_info):
    admin_command_info.guild.get_channel = MagicMock(return_value=None)
    await report(admin_command_info, "a" * 12, make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value="1")
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_forum_channel_early_return(mock_blocked, mock_channel, admin_command_info):
    forum = MagicMock(spec=discord.ForumChannel)
    admin_command_info.guild.get_channel = MagicMock(return_value=forum)
    await report(admin_command_info, "a" * 12, make_target_member())


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value="1")
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_no_bot_send_permission(mock_blocked, mock_channel, admin_command_info):
    ch = admin_command_info.channel
    perms = MagicMock(send_messages=False)
    ch.permissions_for = MagicMock(return_value=perms)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    await report(admin_command_info, "a" * 12, make_target_member())
    admin_command_info.reply.assert_awaited_once()


async def test_report_no_reason(admin_command_info):
    with patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False):
        await report(admin_command_info, "", make_target_member())
    admin_command_info.reply.assert_awaited_once()


async def test_report_reason_too_short(admin_command_info):
    with patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False):
        await report(admin_command_info, "short", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.report_user", new_callable=AsyncMock, return_value=42)
@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock)
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_success(mock_blocked, mock_get_ch, mock_report, admin_command_info):
    ch = admin_command_info.channel
    ch.permissions_for = MagicMock(return_value=MagicMock(send_messages=True))
    ch.send = AsyncMock()
    mock_get_ch.return_value = str(ch.id)
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    admin_command_info.guild.preferred_locale = "en_US"
    await report(admin_command_info, "a" * 12, make_target_member())
    admin_command_info.reply.assert_awaited_once()
    ch.send.assert_awaited_once()
