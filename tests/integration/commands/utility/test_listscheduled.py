from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models import ScheduledMessageModel
from tests.helpers.discord import make_command_info, make_interaction, make_member

pytestmark = pytest.mark.asyncio


GUILD_ID = "123456789012345678"
CHANNEL_ID = "444444444444444444"
USER_ID = "111111111111111111"


def _scheduled_message(**overrides):
    defaults = {
        "message_id": 1,
        "guild_id": GUILD_ID,
        "channel_id": CHANNEL_ID,
        "user_id": USER_ID,
        "content": "Test message content",
        "send_time": datetime(2025, 6, 1, 12, 0, 0),
        "repeat_interval": 3600,
        "repeat_amount": 5,
        "created_at": datetime.now(),
    }
    defaults.update(overrides)
    return ScheduledMessageModel(**defaults)


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_no_messages(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = []
    info = make_command_info()
    await list_scheduled_messages(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("embed") is not None


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_with_messages(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message()]
    info = make_command_info()
    await list_scheduled_messages(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("view") is not None


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_dm_message(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(channel_id=None, guild_id=None)]
    info = make_command_info()
    await list_scheduled_messages(info)
    info.reply.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_list_scheduled_long_content(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(content="x" * 500)]
    info = make_command_info()
    await list_scheduled_messages(info)
    info.reply.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.update_content", new_callable=AsyncMock)
async def test_edit_content_modal_submit(mock_update):
    from commands.utility.listscheduled import EditContentModal

    view = MagicMock()
    view.messages = [_scheduled_message()]
    modal = EditContentModal(message_id=1, current_content="old", locale="en-US", view=view)
    modal.new_content.value = "new content"
    interaction = make_interaction()
    await modal.on_submit(interaction)
    mock_update.assert_awaited_once_with(1, "new content")
    interaction.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_pagination_view_get_embed(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(), _scheduled_message(message_id=2)]
    info = make_command_info()
    await list_scheduled_messages(info)
    view = info.reply.await_args.kwargs["view"]
    embed = view.get_embed()
    assert embed is not None


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_pagination_truncate_content(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(content="short")]
    info = make_command_info()
    await list_scheduled_messages(info)
    view = info.reply.await_args.kwargs["view"]
    truncated = view.truncate_content("a" * 1500)
    assert len(truncated) <= 1000


@patch("commands.utility.listscheduled.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_pagination_cancel_last_message(mock_get, mock_cancel):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message()]
    info = make_command_info()
    await list_scheduled_messages(info)
    view = info.reply.await_args.kwargs["view"]
    cancel_btn = view.children[4]
    interaction = make_interaction(user=info.user)
    interaction.response.edit_message = AsyncMock()
    await cancel_btn.callback(interaction)
    mock_cancel.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_pagination_unauthorized(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(), _scheduled_message(message_id=2)]
    info = make_command_info()
    await list_scheduled_messages(info)
    view = info.reply.await_args.kwargs["view"]
    other = make_member(user_id=999999999)
    interaction = make_interaction(user=other)
    await view.next_page(interaction)
    interaction.response.send_message.assert_awaited_once()


@patch("commands.utility.listscheduled.ScheduledMessageService.get_user_messages", new_callable=AsyncMock)
async def test_pagination_next_page(mock_get):
    from commands.utility.listscheduled import list_scheduled_messages

    mock_get.return_value = [_scheduled_message(), _scheduled_message(message_id=2)]
    info = make_command_info()
    await list_scheduled_messages(info)
    view = info.reply.await_args.kwargs["view"]
    view.update_message = AsyncMock()
    interaction = make_interaction(user=info.user)
    await view.next_page(interaction)
    view.update_message.assert_awaited_once()
    assert view.page == 1
