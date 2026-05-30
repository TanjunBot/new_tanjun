from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from commands.channel.farewell import (
    _process_farewell_image_sync,
    farewellUser,
    removeFarewellChannel,
    setFarewellChannel,
)
from tests.helpers.discord import make_member, make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


@patch(
    "commands.channel.farewell.utility.upload_image_to_imgbb",
    new_callable=AsyncMock,
    return_value={"data": {"url": "http://img"}},
)
@patch("commands.channel.farewell.set_leave_channel", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=None)
async def test_set_farewell_with_attachment(mock_get, mock_set, mock_upload, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    attachment = MagicMock()
    attachment.filename = "bg.gif"
    await setFarewellChannel(admin_command_info, channel, message="bye", image_background=attachment)
    mock_upload.assert_awaited_once()
    mock_set.assert_awaited_once()


@patch("commands.channel.farewell.discord.File", return_value=MagicMock())
@patch("commands.channel.farewell.run_in_executor", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_image_or_gif_frames", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock)
async def test_farewell_user_sends(mock_get_ch, mock_frames, mock_exec, mock_file):
    member = make_member()
    member.display_avatar = MagicMock(url="https://cdn.example/a.png")
    channel = make_text_channel(guild=member.guild)
    channel.send = AsyncMock()
    member.guild.fetch_channel = AsyncMock(return_value=channel)
    cfg = MagicMock()
    cfg.channel_id = str(channel.id)
    cfg.message = "Bye {user}"
    cfg.image_background = "http://bg"
    mock_get_ch.return_value = cfg
    frame = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    mock_frames.side_effect = [([frame], 0), ([frame], 100)]
    mock_exec.return_value = io.BytesIO(b"gif")
    await farewellUser(member)
    channel.send.assert_awaited_once()


async def test_set_farewell_bot_missing_permissions(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(send_messages=False))
    await setFarewellChannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=True)
async def test_set_farewell_already_set(mock_get, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await setFarewellChannel(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.channel.farewell.remove_leave_channel", new_callable=AsyncMock)
@patch("commands.channel.farewell.get_leave_channel", new_callable=AsyncMock, return_value=True)
async def test_remove_farewell_success(mock_get, mock_remove, admin_command_info):
    await removeFarewellChannel(admin_command_info)
    mock_remove.assert_awaited_once()


def test_process_farewell_image_sync():
    user = make_member()
    user.guild.preferred_locale = "en-US"
    user.guild.member_count = 10
    bg = Image.new("RGBA", (600, 400), (50, 50, 50, 255))
    av = Image.new("RGBA", (150, 150), (80, 80, 80, 255))
    out = _process_farewell_image_sync([bg], [av], user, 80)
    assert out.getvalue()
