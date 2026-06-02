"""Tests for services/image_service.py and pillow_service.py."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image

from services import pillow_service
from services.image_service import ImageFilter, ImageOperation, ImageService


class TestImageFilter:
    def test_locale_key(self):
        assert ImageFilter.SHARPEN.locale_key == "sharpen"

    def test_to_pil(self):
        filt = ImageFilter.GAUSSIAN_BLUR.to_pil(radius=5)
        assert filt is not None


class TestImageService:
    def test_validate_attachment_bad_extension(self):
        attachment = MagicMock()
        attachment.filename = "file.exe"
        attachment.size = 1000
        assert ImageService.validate_attachment(attachment) == "typenotsupported"

    def test_validate_attachment_valid(self):
        attachment = MagicMock()
        attachment.url = "https://example.com/image.png"
        attachment.content_type = "image/png"
        attachment.size = 1000
        assert ImageService.validate_attachment(attachment) is None

    @pytest.mark.asyncio
    async def test_process_resize(self):
        img = Image.new("RGB", (100, 100), color="red")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        operation = ImageOperation(resize=(50, 50))
        result = await ImageService.process(buf.getvalue(), operation)
        processed = Image.open(io.BytesIO(result))
        assert processed.size == (50, 50)

    @pytest.mark.asyncio
    async def test_process_mirror(self):
        img = Image.new("RGB", (10, 10), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        operation = ImageOperation(mirror_axis="horizontal")
        result = await ImageService.process(buf.getvalue(), operation)
        assert len(result) > 0

    def test_format_error_embed(self):
        embed = ImageService.format_error_embed("en-US", "error.unknown_filter")
        assert embed is not None

    def test_validate_attachment_filesize(self):
        attachment = MagicMock()
        attachment.filename = "file.png"
        attachment.size = ImageService.MAX_FILE_SIZE + 1
        assert ImageService.validate_attachment(attachment) == "filesize"

    def test_image_filter_format_methods(self):
        with patch("localizer.tanjunLocalizer.localize", return_value="ok"):
            assert ImageFilter.SHARPEN.format_success_title("en") == "ok"
            assert ImageFilter.CONTOUR.format_success_description("en") == "ok"

    @pytest.mark.asyncio
    async def test_process_no_op_returns_original(self):
        data = b"raw"
        result = await ImageService.process(data, ImageOperation())
        assert result == data

    @pytest.mark.asyncio
    async def test_process_invalid_image_raises(self):
        with pytest.raises(ValueError):
            await ImageService.process(b"not-an-image", ImageOperation(resize=(10, 10)))

    @pytest.mark.asyncio
    async def test_process_compress_jpeg(self):
        img = Image.new("RGBA", (20, 20), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        operation = ImageOperation(compress_quality=80)
        result = await ImageService.process(buf.getvalue(), operation)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_process_scale_and_filter(self):
        img = Image.new("RGB", (40, 40), color="green")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        operation = ImageOperation(filter_name=ImageFilter.EMBOSS, scale=0.5, mirror_axis="y")
        result = await ImageService.process(buf.getvalue(), operation)
        assert len(result) > 0


class TestPillowService:
    def test_create_circular_mask(self):
        mask = pillow_service.create_circular_mask((100, 100))
        assert mask.size == (100, 100)

    def test_create_overlay(self):
        overlay = pillow_service.create_overlay((50, 50), (255, 0, 0, 128))
        assert overlay.size == (50, 50)

    def test_get_frames_static(self):
        img = Image.new("RGBA", (10, 10), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        frames, duration, is_animated = pillow_service.get_frames(buf)
        assert len(frames) == 1
        assert is_animated is False

    @pytest.mark.asyncio
    async def test_fetch_image_success(self):
        img = Image.new("RGB", (10, 10))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=buf.getvalue())
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await pillow_service.fetch_image("https://example.com/img.png")
        assert result is not None

    @pytest.mark.asyncio
    async def test_fetch_image_failure(self):
        mock_resp = AsyncMock()
        mock_resp.status = 404
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.get = MagicMock(return_value=mock_resp)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await pillow_service.fetch_image("https://example.com/missing.png")
        assert result is None

    def test_save_optimized_gif(self):
        frames = [Image.new("RGBA", (10, 10), (255, 0, 0, 255))]
        result = pillow_service.save_optimized_gif(frames, duration=100)
        assert isinstance(result, io.BytesIO)
