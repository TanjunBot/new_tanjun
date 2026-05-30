from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from commands.channel.welcome import (
    _process_welcome_image_sync,
    removeWelcomeChannel,
    setWelcomeChannel,
    welcomeNewUser,
)
from tests.helpers.discord import make_member, make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


@patch("commands.channel.welcome.utility.upload_image_to_imgbb", new_callable=AsyncMock, return_value={"data": {"url": "http://img"}})
@patch("commands.channel.welcome.set_welcome_channel", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=None)
async def test_set_welcome_with_attachment(mock_get, mock_set, mock_upload, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    attachment = MagicMock()
    attachment.filename = "bg.png"
    await setWelcomeChannel(admin_command_info, channel, message="hi", image_background=attachment)
    mock_upload.assert_awaited_once()
    mock_set.assert_awaited_once()


async def test_remove_welcome_missing_permission(restricted_command_info):
    await removeWelcomeChannel(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


def test_process_welcome_image_sync():
    user = make_member()
    user.guild.preferred_locale = "en-US"
    user.guild.member_count = 42
    bg = Image.new("RGBA", (600, 400), (100, 100, 100, 255))
    av = Image.new("RGBA", (150, 150), (200, 200, 200, 255))
    result = _process_welcome_image_sync([bg], [av], user, 100)
    assert isinstance(result, io.BytesIO)
    assert result.getvalue()


@patch("commands.channel.welcome.discord.File", return_value=MagicMock())
@patch("commands.channel.welcome.run_in_executor", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_image_or_gif_frames", new_callable=AsyncMock)
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock)
async def test_welcome_new_user_sends(mock_get_ch, mock_frames, mock_exec, mock_file):
    member = make_member()
    member.display_avatar = MagicMock(url="https://cdn.example/a.png")
    channel = make_text_channel(guild=member.guild)
    channel.send = AsyncMock()
    member.guild.fetch_channel = AsyncMock(return_value=channel)
    cfg = MagicMock()
    cfg.channel_id = str(channel.id)
    cfg.message = "Welcome {user} to {guild} (#{member})"
    cfg.image_background = "http://bg"
    mock_get_ch.return_value = cfg
    frame = Image.new("RGBA", (100, 100), (0, 0, 0, 255))
    mock_frames.side_effect = [([frame], 0), ([frame], 100)]
    mock_exec.return_value = io.BytesIO(b"gif")
    await welcomeNewUser(member)
    channel.send.assert_awaited_once()


@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock, return_value=None)
async def test_welcome_new_user_no_config(mock_get):
    member = make_member()
    await welcomeNewUser(member)


@patch("commands.channel.welcome.get_image_or_gif_frames", new_callable=AsyncMock, return_value=([], 0))
@patch("commands.channel.welcome.get_welcome_channel", new_callable=AsyncMock)
async def test_welcome_new_user_missing_frames(mock_get_ch, mock_frames):
    member = make_member()
    cfg = MagicMock(image_background="http://x", message=None)
    mock_get_ch.return_value = cfg
    await welcomeNewUser(member)
