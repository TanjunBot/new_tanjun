from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.image.background import background
from commands.image.compress import compress
from commands.image.mirror import mirror
from commands.image.rescale import rescale

pytestmark = pytest.mark.asyncio


def _image_attachment(content_type="image/png"):
    image = MagicMock()
    image.content_type = content_type
    image.read = AsyncMock(return_value=b"fake-image-data")
    image.filename = "test.png"
    return image


@patch("commands.image.compress.ImageService.process", new_callable=AsyncMock, return_value=b"compressed")
@patch("commands.image.compress.ImageService.validate_attachment", return_value=None)
async def test_compress_success(mock_validate, mock_process, admin_command_info):
    await compress(admin_command_info, _image_attachment(), quality=80)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.compress.ImageService.validate_attachment", return_value="invalid")
async def test_compress_invalid_attachment(mock_validate, admin_command_info):
    await compress(admin_command_info, _image_attachment(), quality=80)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.mirror.ImageService.process", new_callable=AsyncMock, return_value=b"mirrored")
@patch("commands.image.mirror.ImageService.validate_attachment", return_value=None)
async def test_mirror_success(mock_validate, mock_process, admin_command_info):
    await mirror(admin_command_info, _image_attachment(), axis="x")
    admin_command_info.reply.assert_awaited_once()


async def test_mirror_invalid_axis(admin_command_info):
    await mirror(admin_command_info, _image_attachment(), axis="z")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.mirror.ImageService.validate_attachment", return_value="too_large")
async def test_mirror_invalid(mock_validate, admin_command_info):
    await mirror(admin_command_info, _image_attachment(), axis="x")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.rescale.ImageService.process", new_callable=AsyncMock, return_value=b"rescaled")
@patch("commands.image.rescale.ImageService.validate_attachment", return_value=None)
async def test_rescale_success(mock_validate, mock_process, admin_command_info):
    await rescale(admin_command_info, _image_attachment(), factor=0.5)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.rescale.ImageService.validate_attachment", return_value="invalid")
async def test_rescale_invalid(mock_validate, admin_command_info):
    await rescale(admin_command_info, _image_attachment(), factor=0.5)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.background.ImageService.process", new_callable=AsyncMock, return_value=b"bg")
@patch("commands.image.background.ImageService.validate_attachment", return_value=None)
async def test_background_success(mock_validate, mock_process, admin_command_info):
    await background(admin_command_info, _image_attachment())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image.background.ImageService.validate_attachment", return_value="invalid")
async def test_background_invalid(mock_validate, admin_command_info):
    await background(admin_command_info, _image_attachment())
    admin_command_info.reply.assert_awaited_once()
