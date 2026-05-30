from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.trigger_messages.send import send_trigger_message
from tests.helpers.discord import make_message

pytestmark = pytest.mark.asyncio


async def test_send_trigger_no_guild():
    message = make_message()
    message.guild = None
    await send_trigger_message(message)
    message.reply.assert_not_called()


async def test_send_trigger_no_content():
    message = make_message(content="")
    await send_trigger_message(message)
    message.reply.assert_not_called()


@patch("commands.admin.trigger_messages.send.trigger_message_service")
async def test_send_trigger_no_match(mock_service):
    mock_service.match = AsyncMock(return_value=None)
    message = make_message(content="hello")
    await send_trigger_message(message)
    message.reply.assert_not_called()


@patch("commands.admin.trigger_messages.send.check_if_opted_out", new_callable=AsyncMock, return_value=True)
@patch("commands.admin.trigger_messages.send.trigger_message_service")
async def test_send_trigger_opted_out(mock_service, mock_optout):
    trigger = MagicMock()
    trigger.response = "response"
    mock_service.match = AsyncMock(return_value=trigger)
    message = make_message(content="trigger")
    await send_trigger_message(message)
    message.reply.assert_not_called()


@patch("commands.admin.trigger_messages.send.check_if_opted_out", new_callable=AsyncMock, return_value=False)
@patch("commands.admin.trigger_messages.send.trigger_message_service")
async def test_send_trigger_success(mock_service, mock_optout):
    trigger = MagicMock()
    trigger.response = "auto reply"
    mock_service.match = AsyncMock(return_value=trigger)
    message = make_message(content="trigger")
    await send_trigger_message(message)
    message.reply.assert_awaited_once_with("auto reply")


async def test_send_trigger_no_channel():
    message = make_message()
    message.channel = None
    await send_trigger_message(message)
    message.reply.assert_not_called()
