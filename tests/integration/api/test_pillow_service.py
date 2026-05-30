from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image, ImageDraw

import tests.mock_config as mock_config

mock_config.patch_config_module()

from services import pillow_service
from services.pillow_service import (
    _extend_and_trim,
    _normalize_frame_count,
    _quantize_frames,
    create_circular_mask,
    create_overlay,
    draw_rounded_rectangle,
    fetch_image,
    get_frames,
    get_image_or_gif_frames,
    load_font,
    process_frames_with_mask,
    run_in_executor,
    save_optimized_gif,
)


def _rgba(size=(40, 40), color=(255, 0, 0, 255)):
    return Image.new("RGBA", size, color)


def _png_bytes(size=(20, 20), color=(0, 128, 255, 255)):
    buf = io.BytesIO()
    _rgba(size, color).save(buf, format="PNG")
    buf.seek(0)
    return buf


class TestFrameHelpers:
    def test_normalize_frame_count_with_extra_lists(self):
        bg = [_rgba()]
        av = [_rgba(), _rgba()]
        extra = [[_rgba(), _rgba(), _rgba()]]
        assert _normalize_frame_count(bg, av, extra) == 3

    def test_extend_and_trim_repeats_short_list(self):
        frames = [_rgba()]
        extended = _extend_and_trim(frames, 4)
        assert len(extended) == 4

    def test_extend_and_trim_trims_long_list(self):
        frames = [_rgba() for _ in range(6)]
        trimmed = _extend_and_trim(frames, 3)
        assert len(trimmed) == 3

    def test_quantize_single_frame_returns_unchanged(self):
        frame = _rgba()
        assert _quantize_frames([frame]) == [frame]

    def test_quantize_frames_without_palette_data(self):
        frames = [Image.new("RGB", (10, 10), (255, 0, 0)) for _ in range(3)]
        with patch.object(Image.Image, "quantize", side_effect=[MagicMock(getpalette=MagicMock(return_value=None))]):
            result = _quantize_frames(frames)
        assert result == frames


class TestCircularMask:
    def test_mask_size_matches_input(self):
        mask = create_circular_mask((50, 60))
        assert mask.size == (50, 60)
        assert mask.mode == "L"

    def test_center_pixel_is_opaque(self):
        mask = create_circular_mask((40, 40))
        assert mask.getpixel((20, 20)) == 255


class TestDrawRoundedRectangle:
    def test_fill_only(self):
        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_rounded_rectangle(draw, (10, 10, 90, 90), radius=10, fill=(255, 255, 255, 128))
        assert img.getpixel((50, 50))[3] > 0

    def test_with_outline(self):
        img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_rounded_rectangle(
            draw,
            (10, 10, 90, 90),
            radius=10,
            fill=(255, 255, 255, 255),
            outline=(0, 0, 0, 255),
            width=2,
        )
        assert img.getpixel((50, 50))[0] == 255


class TestFetchImage:
    @pytest.mark.asyncio
    async def test_returns_bytes_on_success(self):
        payload = _png_bytes().read()
        response = AsyncMock(status=200, read=AsyncMock(return_value=payload))
        response.__aenter__ = AsyncMock(return_value=response)
        response.__aexit__ = AsyncMock(return_value=None)
        session = MagicMock()
        session.get = MagicMock(return_value=response)
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        with patch("services.pillow_service.aiohttp.ClientSession", return_value=session):
            result = await fetch_image("https://example.com/img.png")
        assert isinstance(result, io.BytesIO)

    @pytest.mark.asyncio
    async def test_returns_none_on_bad_status(self):
        response = AsyncMock(status=404, read=AsyncMock(return_value=b""))
        response.__aenter__ = AsyncMock(return_value=response)
        response.__aexit__ = AsyncMock(return_value=None)
        session = MagicMock()
        session.get = MagicMock(return_value=response)
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        with patch("services.pillow_service.aiohttp.ClientSession", return_value=session):
            assert await fetch_image("https://example.com/missing.png") is None

    @pytest.mark.asyncio
    async def test_returns_none_on_client_error(self):
        import aiohttp

        session = MagicMock()
        session.get = MagicMock(side_effect=aiohttp.ClientError("network"))
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=None)
        with patch("services.pillow_service.aiohttp.ClientSession", return_value=session):
            assert await fetch_image("https://example.com/err.png") is None


class TestGetFrames:
    def test_static_image_single_frame(self):
        frames, duration, animated = get_frames(_png_bytes())
        assert len(frames) == 1
        assert animated is False
        assert duration == 100
        assert frames[0].mode == "RGBA"

    def test_invalid_data_returns_empty(self):
        frames, duration, animated = get_frames(io.BytesIO(b"not-an-image"))
        assert frames == []
        assert duration == 0
        assert animated is False

    def test_animated_gif_multiple_frames(self):
        buf = io.BytesIO()
        f1 = _rgba((10, 10), (255, 0, 0, 255))
        f2 = _rgba((10, 10), (0, 255, 0, 255))
        f1.save(buf, format="GIF", save_all=True, append_images=[f2], duration=50, loop=0)
        buf.seek(0)
        frames, duration, animated = get_frames(buf)
        assert len(frames) >= 2
        assert animated is True
        assert duration == 50


class TestGetImageOrGifFrames:
    @pytest.mark.asyncio
    async def test_delegates_to_fetch_and_get_frames(self):
        with patch("services.pillow_service.fetch_image", new=AsyncMock(return_value=_png_bytes())):
            frames, duration = await get_image_or_gif_frames("https://example.com/a.png")
        assert len(frames) == 1
        assert duration == 100

    @pytest.mark.asyncio
    async def test_returns_empty_when_fetch_fails(self):
        with patch("services.pillow_service.fetch_image", new=AsyncMock(return_value=None)):
            frames, duration = await get_image_or_gif_frames("https://example.com/b.png")
        assert frames == []
        assert duration == 0


class TestOverlayAndGif:
    def test_create_overlay_fill(self):
        overlay = create_overlay((80, 60), (10, 20, 30, 100))
        assert overlay.size == (80, 60)
        assert overlay.getpixel((40, 30))[3] == 100

    def test_save_optimized_gif_empty(self):
        buf = save_optimized_gif([], duration=100)
        assert buf.tell() == 0

    def test_save_optimized_gif_single_frame_no_quantize(self):
        buf = save_optimized_gif([_rgba()], duration=80, quantize=False)
        assert buf.getvalue()[:6] == b"GIF89a"

    def test_save_optimized_gif_multi_frame_quantized(self):
        frames = [Image.new("RGB", (20, 20), (i * 20, 0, 0)) for i in range(1, 5)]
        buf = save_optimized_gif(frames, duration=50, quantize=True, loop=2)
        assert len(buf.getvalue()) > 0

    def test_save_optimized_gif_extends_short_frame_list(self):
        frames = [_rgba(), _rgba((30, 30), (0, 255, 0, 255))]
        buf = save_optimized_gif(frames, duration=40, quantize=False)
        assert buf.getvalue().startswith(b"GIF")


class TestProcessFramesWithMask:
    def test_pastes_through_mask(self):
        bg = _rgba((60, 60), (255, 255, 255, 255))
        avatar = _rgba((20, 20), (0, 0, 255, 255))
        mask = create_circular_mask((20, 20))
        result = process_frames_with_mask([bg], mask, [(avatar, (10, 10))])
        assert len(result) == 1
        assert result[0].size == (60, 60)


class TestLoadFont:
    def test_load_font_missing_raises(self):
        with pytest.raises(OSError):
            load_font("/nonexistent/font.ttf", 12)

    def test_load_font_with_matplotlib_font(self):
        import matplotlib.font_manager as fm

        path = fm.findfont(fm.FontProperties())
        font = load_font(path, 14)
        assert font.size == 14


class TestRunInExecutor:
    @pytest.mark.asyncio
    async def test_runs_callable_in_executor(self):
        def add(a: int, b: int) -> int:
            return a + b

        result = await run_in_executor(add, 2, 3)
        assert result == 5

    @pytest.mark.asyncio
    async def test_executor_uses_module_pool(self):
        assert pillow_service._PILLOW_SERVICE_EXECUTOR is not None
