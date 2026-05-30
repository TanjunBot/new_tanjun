from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.level.level_rankcard import set_background_command, show_rankcard_command
from tests.helpers.discord import make_target_member

pytestmark = pytest.mark.asyncio


@patch("commands.level.level_rankcard.generate_rankcard", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.get_user_level_info", new_callable=AsyncMock)
async def test_show_rankcard(mock_info, mock_gen, admin_command_info):
    mock_info.return_value = MagicMock()
    mock_gen.return_value = MagicMock()
    user = make_target_member()
    await show_rankcard_command(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


async def test_set_background_invalid_format(admin_command_info):
    image = MagicMock()
    image.content_type = "text/plain"
    await set_background_command(admin_command_info, image)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_rankcard.upload_image_to_imgbb", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.set_custom_background", new_callable=AsyncMock)
async def test_set_background_success(mock_set, mock_upload, admin_command_info):
    image = MagicMock()
    image.content_type = "image/png"
    image.read = AsyncMock(return_value=b"data")
    mock_upload.return_value = {"data": {"url": "http://example.com/bg.png"}}
    await set_background_command(admin_command_info, image)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_rankcard.get_user_level_info", new_callable=AsyncMock, return_value=None)
async def test_show_rankcard_no_data(mock_info, admin_command_info):
    user = make_target_member()
    await show_rankcard_command(admin_command_info, user)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_rankcard.upload_image_to_imgbb", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.set_custom_background", new_callable=AsyncMock)
async def test_set_background_guild_id(mock_set, mock_upload, admin_command_info):
    image = MagicMock()
    image.content_type = "image/jpeg"
    image.read = AsyncMock(return_value=b"data")
    mock_upload.return_value = {"data": {"url": "http://example.com/bg.jpg"}}
    await set_background_command(admin_command_info, image)
    mock_set.assert_awaited_once_with(
        str(admin_command_info.guild.id), str(admin_command_info.user.id), "http://example.com/bg.jpg"
    )
