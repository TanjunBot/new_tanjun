from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.utility.report import report, report_btn_click
from commands.utility.removescheduled import MessageSelectView, remove_scheduled_message
from tests.helpers.discord import make_permissions, make_target_member, make_text_channel
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


async def test_report_guild_only(admin_command_info):
    admin_command_info.guild = None
    await report(admin_command_info, "reason long enough", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=True)
async def test_report_blocked_reporter(mock_blocked, admin_command_info):
    await report(admin_command_info, "reason long enough", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value=None)
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_no_channel(mock_blocked, mock_channel, admin_command_info):
    await report(admin_command_info, "reason long enough", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value="999999999")
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_channel_not_found(mock_blocked, mock_channel, admin_command_info):
    admin_command_info.guild.get_channel = MagicMock(return_value=None)
    await report(admin_command_info, "reason long enough", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.get_report_channel", new_callable=AsyncMock, return_value="999999999")
@patch("commands.utility.report.check_if_reporter_is_blocked", new_callable=AsyncMock, return_value=False)
async def test_report_no_send_permission(mock_blocked, mock_channel, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    admin_command_info.guild.get_channel = MagicMock(return_value=ch)
    await report(admin_command_info, "reason long enough", make_target_member())
    admin_command_info.reply.assert_awaited_once()


async def test_report_no_reason(admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    with (
        patch("commands.utility.report.check_if_reporter_is_blocked", AsyncMock(return_value=False)),
        patch("commands.utility.report.get_report_channel", AsyncMock(return_value=str(ch.id))),
    ):
        admin_command_info.guild.get_channel = MagicMock(return_value=ch)
        await report(admin_command_info, "", make_target_member())
    admin_command_info.reply.assert_awaited_once()


async def test_report_reason_too_short(admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    with (
        patch("commands.utility.report.check_if_reporter_is_blocked", AsyncMock(return_value=False)),
        patch("commands.utility.report.get_report_channel", AsyncMock(return_value=str(ch.id))),
    ):
        admin_command_info.guild.get_channel = MagicMock(return_value=ch)
        await report(admin_command_info, "short", make_target_member())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.report.report_user", new_callable=AsyncMock, return_value=1)
async def test_report_success(mock_report, admin_command_info):
    ch = make_text_channel(guild=admin_command_info.guild)
    ch.send = AsyncMock()
    ch.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    with (
        patch("commands.utility.report.check_if_reporter_is_blocked", AsyncMock(return_value=False)),
        patch("commands.utility.report.get_report_channel", AsyncMock(return_value=str(ch.id))),
    ):
        admin_command_info.guild.get_channel = MagicMock(return_value=ch)
        await report(admin_command_info, "reason long enough", make_target_member())
    ch.send.assert_awaited_once()
    assert admin_command_info.reply.await_count >= 1


async def test_report_btn_no_permission():
    interaction = make_view_interaction()
    interaction.channel = make_text_channel()
    interaction.guild = interaction.channel.guild
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
    await report_btn_click(interaction, "report_accept;1;2")
    interaction.response.send_message.assert_awaited_once()


@patch("commands.utility.report.accept_report", new_callable=AsyncMock)
async def test_report_btn_accept(mock_accept):
    interaction = make_view_interaction()
    interaction.channel = make_text_channel()
    interaction.guild = interaction.channel.guild
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
    await report_btn_click(interaction, "report_accept;1;2")
    mock_accept.assert_awaited_once()


@patch("commands.utility.report.reject_report", new_callable=AsyncMock)
async def test_report_btn_reject(mock_reject):
    interaction = make_view_interaction()
    interaction.channel = make_text_channel()
    interaction.guild = interaction.channel.guild
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
    await report_btn_click(interaction, "report_reject;1;2")
    mock_reject.assert_awaited_once()


@patch("commands.utility.report.block_reporter", new_callable=AsyncMock)
async def test_report_btn_block(mock_block):
    interaction = make_view_interaction()
    interaction.channel = make_text_channel()
    interaction.guild = interaction.channel.guild
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
    await report_btn_click(interaction, "report_block_reporter;1;2")
    mock_block.assert_awaited_once()


async def test_report_btn_invalid():
    interaction = make_view_interaction()
    interaction.channel = make_text_channel()
    interaction.guild = interaction.channel.guild
    interaction.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=True))
    await report_btn_click(interaction, "report_unknown;1;2")
    interaction.response.send_message.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock, return_value=[])
async def test_remove_scheduled_no_messages(mock_get, admin_command_info):
    await remove_scheduled_message(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.removescheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_remove_scheduled_by_id_success(mock_get, mock_cancel, admin_command_info):
    from models import ScheduledMessageModel

    dt = datetime.now(timezone.utc)
    msg = ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hello", dt, None, None, None, None, dt))
    mock_get.return_value = [msg]
    await remove_scheduled_message(admin_command_info, message_id=1)
    mock_cancel.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_remove_scheduled_not_found(mock_get, admin_command_info):
    from models import ScheduledMessageModel

    dt = datetime.now(timezone.utc)
    msg = ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hello", dt, None, None, None, None, dt))
    mock_get.return_value = [msg]
    await remove_scheduled_message(admin_command_info, message_id=999)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.removescheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_remove_scheduled_select_view(mock_get, admin_command_info):
    from models import ScheduledMessageModel

    dt = datetime.now(timezone.utc)
    msg = ScheduledMessageModel.from_row((1, GUILD_ID, CHANNEL_ID, USER_ID, "hello world", dt, None, None, None, None, dt))
    mock_get.return_value = [msg]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await remove_scheduled_message(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_scheduled_view_timeout():
    view = MessageSelectView([], "en")
    msg = MagicMock()
    msg.edit = AsyncMock()
    view.set_message(msg)
    await view.on_timeout()
    msg.edit.assert_awaited_once()
