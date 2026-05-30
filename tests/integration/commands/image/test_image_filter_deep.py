from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.image import _filter
from services.image_service import ImageFilter, ImageOperation


pytestmark = pytest.mark.asyncio


def _attachment(filename: str = "test.png", size: int = 100) -> MagicMock:
    att = MagicMock()
    att.filename = filename
    att.size = size
    att.read = AsyncMock(return_value=b"png-bytes")
    return att


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_contour_success(mock_process, admin_command_info):
    await _filter.contour(admin_command_info, _attachment())
    admin_command_info.reply.assert_awaited_once()
    mock_process.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_sharpen_success(mock_process, admin_command_info):
    await _filter.sharpen(admin_command_info, _attachment())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
@pytest.mark.parametrize(
    "func",
    [
        _filter.detail,
        _filter.edge_enhance,
        _filter.emboss,
        _filter.find_edges,
        _filter.smooth,
    ],
)
async def test_filter_wrappers(mock_process, func, admin_command_info):
    await func(admin_command_info, _attachment())
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_apply_filter_success(mock_process, admin_command_info):
    await _filter.apply_filter(admin_command_info, _attachment(), "contour")
    admin_command_info.reply.assert_awaited_once()


async def test_apply_filter_unknown(admin_command_info):
    await _filter.apply_filter(admin_command_info, _attachment(), "not-a-filter")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.validate_attachment", return_value="filesize")
async def test_validate_and_process_error(mock_validate, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(filter_name=ImageFilter.CONTOUR),
    )
    admin_command_info.reply.assert_awaited_once()
    mock_validate.assert_called_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"jpeg")
async def test_validate_and_process_compress(mock_process, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(compress_quality=80),
        success_locale_prefix="image.compress",
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_validate_and_process_mirror(mock_process, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(mirror_axis="x"),
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_validate_and_process_resize(mock_process, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(resize=(100, 100)),
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_validate_and_process_scale(mock_process, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(scale=0.5),
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out")
async def test_validate_and_process_remove_background(mock_process, admin_command_info):
    await _filter._validate_and_process(
        admin_command_info,
        _attachment(),
        ImageOperation(remove_background=True),
    )
    admin_command_info.reply.assert_awaited_once()


@patch("commands.image._filter.ImageService.validate_attachment", return_value="typenotsupported")
async def test_apply_filter_validation_error(mock_validate, admin_command_info):
    await _filter.apply_filter(admin_command_info, _attachment("test.gif"), "contour")
    admin_command_info.reply.assert_awaited_once()
