from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated  # noqa: F401
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.scheduled_message_service import ScheduleMessageParams
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel

ScheduleMessageParams.model_rebuild()

pytestmark = pytest.mark.asyncio

GUILD_ID = "123456789012345678"
CHANNEL_ID = "444444444444444444"
USER_ID = "111111111111111111"


def _info(**kwargs):
    guild = make_guild(guild_id=int(GUILD_ID))
    channel = make_text_channel(channel_id=int(CHANNEL_ID), guild=guild)
    perms = make_permissions(manage_messages=True, send_messages=True)
    user = make_member(user_id=int(USER_ID))
    user.guild_permissions = perms
    user.create_dm = AsyncMock(return_value=MagicMock())
    channel.permissions_for = MagicMock(return_value=perms)
    guild.me.guild_permissions = perms
    client = MagicMock()
    client.user = MagicMock(id=int(USER_ID))
    return make_command_info(user=user, guild=guild, channel=channel, client=client, **kwargs)


def _target_channel(info):
    target = make_text_channel(channel_id=int(CHANNEL_ID) + 1, guild=info.guild)
    target.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    return target


async def test_schedule_message_no_channel():
    from commands.utility.schedulemessage import schedule_message

    info = make_command_info()
    info.channel = None
    await schedule_message(info, "hello", "1h")
    info.reply.assert_awaited_once()


async def test_schedule_message_invalid_time():
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    await schedule_message(info, "hello", "not-a-time", channel=_target_channel(info))
    info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.utility.relativeTimeStrToDate")
async def test_schedule_message_past_time(mock_time):
    from commands.utility.schedulemessage import schedule_message

    mock_time.return_value = datetime.now() - timedelta(hours=1)
    info = _info()
    await schedule_message(info, "hello", "1h", channel=_target_channel(info))
    info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.schedule", new_callable=AsyncMock)
async def test_schedule_message_success(mock_schedule):
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    await schedule_message(info, "hello", "1h", channel=_target_channel(info))
    info.reply.assert_awaited_once()
    mock_schedule.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.schedule", new_callable=AsyncMock)
async def test_schedule_message_success_with_channel(mock_schedule):
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    target = _target_channel(info)
    await schedule_message(info, "hello", "1h", channel=target)
    info.reply.assert_awaited_once()
    mock_schedule.assert_awaited_once()


async def test_schedule_message_no_channel_permission():
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    target = _target_channel(info)
    no_send = make_permissions(send_messages=False)
    target.permissions_for = MagicMock(return_value=no_send)
    await schedule_message(info, "hello", "1h", channel=target)
    info.reply.assert_awaited_once()


async def test_schedule_message_no_bot_channel_permission():
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    target = _target_channel(info)
    user_perms = make_permissions(send_messages=True)
    bot_no_send = make_permissions(send_messages=False)
    target.permissions_for = MagicMock(side_effect=lambda m: user_perms if m == info.user else bot_no_send)
    await schedule_message(info, "hello", "1h", channel=target)
    info.reply.assert_awaited_once()


async def test_schedule_message_no_repeat_permission():
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    no_manage = make_permissions(manage_messages=False, send_messages=True)
    info.channel.permissions_for = MagicMock(return_value=no_manage)
    target = _target_channel(info)
    target.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await schedule_message(info, "hello", "1h", channel=target, repeat="1d")
    info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.get_upcoming", new_callable=AsyncMock)
async def test_schedule_message_too_many_scheduled(mock_upcoming):
    from commands.utility.schedulemessage import schedule_message

    mock_upcoming.return_value = [MagicMock()]
    info = _info()
    no_manage = make_permissions(manage_messages=False, send_messages=True)
    info.channel.permissions_for = MagicMock(return_value=no_manage)
    target = _target_channel(info)
    target.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    await schedule_message(info, "hello", "1h", channel=target)
    info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.schedule", new_callable=AsyncMock)
async def test_schedule_message_dm_success(mock_schedule):
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    dm = MagicMock()
    dm.permissions_for = MagicMock(return_value=make_permissions(send_messages=True))
    info.user.create_dm = AsyncMock(return_value=dm)
    await schedule_message(info, "hello", "1h", channel=None)
    info.reply.assert_awaited_once()
    mock_schedule.assert_awaited_once()


async def test_schedule_message_no_dm_permission():
    from commands.utility.schedulemessage import schedule_message

    info = _info()
    dm = MagicMock()
    dm.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    info.user.create_dm = AsyncMock(return_value=dm)
    await schedule_message(info, "hello", "1h", channel=None)
    info.reply.assert_awaited_once()


@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_messages_none(mock_due):
    from commands.utility.schedulemessage import send_scheduled_messages

    mock_due.return_value = None
    client = MagicMock()
    await send_scheduled_messages(client)


@patch("commands.utility.schedulemessage.ScheduledMessageService.cancel", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.update_discord_message_id", new_callable=AsyncMock)
@patch("commands.utility.schedulemessage.ScheduledMessageService.get_due_messages", new_callable=AsyncMock)
async def test_send_scheduled_messages_guild(mock_due, mock_update, mock_cancel):
    from commands.utility.schedulemessage import send_scheduled_messages
    from models import ScheduledMessageModel

    msg = ScheduledMessageModel(
        message_id=1,
        guild_id=GUILD_ID,
        channel_id=CHANNEL_ID,
        user_id=USER_ID,
        content="scheduled",
        send_time=datetime.now(),
        repeat_interval=None,
        repeat_amount=None,
        created_at=datetime.now(),
    )
    mock_due.return_value = [msg]
    guild = make_guild(guild_id=int(GUILD_ID))
    channel = make_text_channel(channel_id=int(CHANNEL_ID), guild=guild)
    channel.send = AsyncMock(return_value=MagicMock(id=999))
    guild.get_channel = MagicMock(return_value=channel)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    await send_scheduled_messages(client)
    channel.send.assert_awaited_once()
    mock_cancel.assert_awaited_once()
