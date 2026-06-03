from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.channel.welcome import setWelcomeChannel
from commands.channel.farewell import setFarewellChannel
from tests.helpers.view_state import embed_from_reply

pytestmark = pytest.mark.asyncio


@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=None)
@patch("commands.channel.welcome.set_welcome_channel", new_callable=AsyncMock)
async def test_set_welcome_channel_success_embed(mock_set, mock_get, admin_command_info) -> None:
    channel = admin_command_info.channel
    channel.permissions_for = MagicMock(return_value=MagicMock(send_messages=True, embed_links=True, attach_files=True))
    admin_command_info.guild.me = admin_command_info.user
    await setWelcomeChannel(admin_command_info, channel, message="hi {user}")
    embed_from_reply(admin_command_info)
    mock_set.assert_awaited_once()


async def test_set_welcome_missing_permission(restricted_command_info) -> None:
    await setWelcomeChannel(restricted_command_info, restricted_command_info.channel)
    embed_from_reply(restricted_command_info)


@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=None)
@patch("commands.channel.farewell.set_leave_channel", new_callable=AsyncMock)
async def test_set_farewell_channel_embed(mock_set, mock_get, admin_command_info) -> None:
    channel = admin_command_info.channel
    channel.permissions_for = MagicMock(return_value=MagicMock(send_messages=True, embed_links=True, attach_files=True))
    admin_command_info.guild.me = admin_command_info.user
    await setFarewellChannel(admin_command_info, channel, message="bye")
    embed_from_reply(admin_command_info)
