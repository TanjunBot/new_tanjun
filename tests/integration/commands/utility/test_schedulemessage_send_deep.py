from __future__ import annotations

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.utility.schedulemessage import send_scheduled_messages
from models import ScheduledMessageModel
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID

pytestmark = pytest.mark.asyncio


def _due_msg(**kwargs) -> ScheduledMessageModel:
    dt = datetime.now()
    row = (
        kwargs.get("message_id", 1),
        kwargs.get("guild_id", str(GUILD_ID)),
        kwargs.get("channel_id", str(CHANNEL_ID)),
        str(USER_ID),
        kwargs.get("content", "hello"),
        dt,
        kwargs.get("repeat_interval"),
        kwargs.get("repeat_amount"),
        kwargs.get("attachments"),
        None,
        dt,
    )
    return ScheduledMessageModel.from_row(row)


@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock, return_value=None)
async def test_send_scheduled_none(mock_due):
    client = MagicMock()
    await send_scheduled_messages(client)
    client.get_guild.assert_not_called()


@patch("commands.utility.schedulemessage.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_guild_channel(mock_due, mock_update_id, mock_cancel):
    msg = _due_msg()
    mock_due.return_value = [msg]
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock(id=999))
    guild = MagicMock()
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await send_scheduled_messages(client)
    channel.send.assert_awaited_once()
    mock_cancel.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.update_send_time", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_infinite_repeat(mock_due, mock_update_id, mock_update_time):
    past = datetime.now() - timedelta(hours=2)
    msg = _due_msg(repeat_interval=3600, repeat_amount=None)
    msg.send_time = past
    mock_due.return_value = [msg]
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock(id=1))
    guild = MagicMock()
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await send_scheduled_messages(client)
    mock_update_time.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.update_repeat_and_send_time", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_finite_repeat(mock_due, mock_update_id, mock_update_repeat, mock_cancel):
    msg = _due_msg(repeat_interval=3600, repeat_amount=5)
    msg.send_time = datetime.now() - timedelta(minutes=1)
    mock_due.return_value = [msg]
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock(id=1))
    guild = MagicMock()
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await send_scheduled_messages(client)
    mock_update_repeat.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_dm(mock_due):
    msg = _due_msg(guild_id=None, channel_id=None)
    mock_due.return_value = [msg]
    user = MagicMock()
    user.dm_channel = MagicMock()
    user.dm_channel.send = AsyncMock(return_value=MagicMock(id=1))
    client = MagicMock()
    client.fetch_user = AsyncMock(return_value=user)
    with (
        patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", AsyncMock()),
        patch("commands.utility.schedulemessage.ScheduledMessageService.cancel", AsyncMock()),
    ):
        await send_scheduled_messages(client)
    user.dm_channel.send.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_with_attachments(mock_due):
    att = json.dumps([{"url": "https://example.com/f.png", "filename": "f.png"}])
    msg = _due_msg(attachments=att)
    mock_due.return_value = [msg]
    channel = MagicMock()
    channel.send = AsyncMock(return_value=MagicMock(id=1))
    guild = MagicMock()
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.read = AsyncMock(return_value=b"data")
    mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_resp.__aexit__ = AsyncMock(return_value=None)
    session = AsyncMock()
    session.get = MagicMock(return_value=mock_resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    with (
        patch("commands.utility.schedulemessage.aiohttp.ClientSession", return_value=session),
        patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", AsyncMock()),
        patch("commands.utility.schedulemessage.ScheduledMessageService.cancel", AsyncMock()),
    ):
        await send_scheduled_messages(client)
    channel.send.assert_awaited_once()
