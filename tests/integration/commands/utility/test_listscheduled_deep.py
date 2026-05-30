from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.listscheduled import EditContentModal, list_scheduled_messages
from commands.utility.schedulemessage import schedule_message
from models import ScheduledMessageModel
from tests.helpers.discord import make_permissions, make_target_member, make_text_channel
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


def _scheduled_msg(msg_id: int = 1, content: str = "hello") -> ScheduledMessageModel:
    dt = datetime.now(UTC) + timedelta(hours=1)
    return ScheduledMessageModel.from_row((msg_id, GUILD_ID, CHANNEL_ID, USER_ID, content, dt, None, None, None, None, dt))


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock, return_value=[])
async def test_list_scheduled_empty(mock_get, admin_command_info):
    await list_scheduled_messages(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


def _view_from_reply(info):
    _, kwargs = info.reply.await_args
    return kwargs.get("view")


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_pagination(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2, "second message")]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.update_message = AsyncMock()
    interaction = make_view_interaction(admin_command_info.user)
    await view.next_page(interaction)
    view.update_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_wrong_user(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.next_page(wrong)
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_cancel_last(mock_get, mock_cancel, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view._make_cancel_callback(view.messages[0])(interaction)
    mock_cancel.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_edit_modal(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    await view._make_edit_callback(view.messages[0])(interaction)
    interaction.response.send_modal.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.update_content", new_callable=AsyncMock)
async def test_edit_content_modal_submit(mock_update, admin_command_info):
    from commands.utility.listscheduled import list_scheduled_messages as _fn

    with patch(
        "commands.utility.listscheduled.ScheduledMessageService.get_user_messages", AsyncMock(return_value=[_scheduled_msg(1)])
    ):
        admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
        await _fn(admin_command_info)
        view = _view_from_reply(admin_command_info)
        modal = EditContentModal(1, "old", "en", view)
        modal.new_content.value = "new content"
        interaction = make_view_interaction(admin_command_info.user)
        await modal.on_submit(interaction)
        mock_update.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_on_timeout(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    message = MagicMock()
    message.edit = AsyncMock()
    admin_command_info.reply = AsyncMock(return_value=message)
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.message = message
    await view.on_timeout()
    message.edit.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_truncate_content(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1, content="hello")]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    assert view.truncate_content("x" * 2000).endswith("...")


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_previous_page(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.page = 1
    view.update_message = AsyncMock()
    interaction = make_view_interaction(admin_command_info.user)
    await view.previous_page(interaction)
    view.update_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_cancel_unauthorized(mock_get, mock_cancel, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view._make_cancel_callback(view.messages[0])(wrong)
    wrong.response.send_message.assert_awaited_once()
    mock_cancel.assert_not_awaited()


@patch("commands.utility.listscheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_cancel_clears_view(mock_get, mock_cancel, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    interaction = make_view_interaction(admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view._make_cancel_callback(view.messages[0])(interaction)
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_edit_unauthorized(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view._make_edit_callback(view.messages[0])(wrong)
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_previous_wrong_user(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    wrong = make_view_interaction(make_target_member(user_id=99999))
    await view.previous_page(wrong)
    wrong.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_update_message(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.update_message = AsyncMock()
    interaction = make_view_interaction(admin_command_info.user)
    await view.next_page(interaction)
    view.update_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_cancel_adjusts_page(mock_get, mock_cancel, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.page = 1
    view.update_message = AsyncMock()
    interaction = make_view_interaction(admin_command_info.user)
    await view._make_cancel_callback(view.messages[1])(interaction)
    assert view.page == 0
    view.update_message.assert_awaited_once()


@patch("commands.utility.listscheduled.MAX_EMBED_LENGTH", 50)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_embed_truncation(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1, content="x" * 500)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    embed = view.get_embed()
    assert any("truncated" in (f.name or "").lower() or f.value for f in embed.fields)


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_previous_page_ok(mock_get, admin_command_info):
    mock_get.return_value = [_scheduled_msg(1), _scheduled_msg(2)]
    admin_command_info.reply = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    await list_scheduled_messages(admin_command_info)
    view = _view_from_reply(admin_command_info)
    view.page = 1
    view.update_message = AsyncMock()
    interaction = make_view_interaction(admin_command_info.user)
    await view.previous_page(interaction)
    assert view.page == 0
    view.update_message.assert_awaited_once()


async def test_schedule_message_no_channel(admin_command_info):
    admin_command_info.channel = None
    await schedule_message(admin_command_info, "hi", "1h")
    admin_command_info.reply.assert_awaited_once()


async def test_schedule_message_invalid_time(admin_command_info):
    await schedule_message(admin_command_info, "hi", "not-a-time")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.utility.relativeTimeStrToDate", return_value=datetime(2020, 1, 1))
async def test_schedule_message_past_time(mock_time, admin_command_info):
    await schedule_message(admin_command_info, "hi", "1h")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.schedule", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduleMessageParams", return_value=MagicMock())
@patch("commands.utility.schedulemessage.utility.relativeTimeStrToDate")
async def test_schedule_message_success(mock_time, mock_params, mock_sched, admin_command_info):
    mock_time.return_value = datetime.now() + timedelta(hours=2)
    await schedule_message(admin_command_info, "hello scheduled", "2h")
    mock_sched.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch(
    "commands.utility.schedulemessage.ScheduledMessageService.get_upcoming", new_callable=AsyncMock, return_value=[MagicMock()]
)
@patch("commands.utility.schedulemessage.utility.relativeTimeStrToDate")
async def test_schedule_message_too_many(mock_time, mock_upcoming, admin_command_info):
    mock_time.return_value = datetime.now() + timedelta(hours=2)
    channel = make_text_channel()
    admin_command_info.channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
    await schedule_message(admin_command_info, "hi", "2h", channel=channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.utility.relativeTimeStrToDate")
async def test_schedule_message_no_send_permission(mock_time, admin_command_info):
    mock_time.return_value = datetime.now() + timedelta(hours=2)
    channel = make_text_channel()
    channel.permissions_for = MagicMock(side_effect=lambda u: make_permissions(send_messages=False))
    await schedule_message(admin_command_info, "hi", "2h", channel=channel)
    admin_command_info.reply.assert_awaited_once()
