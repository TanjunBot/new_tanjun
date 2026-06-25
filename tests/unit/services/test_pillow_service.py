"""Tests for services/pillow_service.py pure helpers."""

from __future__ import annotations

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PIL import Image, ImageDraw

from services import pillow_service

pytestmark = pytest.mark.unit


def _rgba(size: tuple[int, int] = (10, 10), color: tuple[int, int, int, int] = (255, 0, 0, 255)) -> Image.Image:
    return Image.new("RGBA", size, color)


def test_create_circular_mask() -> None:
    mask = pillow_service.create_circular_mask((20, 20))
    assert mask.mode == "L"
    assert mask.size == (20, 20)
    assert mask.getpixel((10, 10)) == 255
    assert mask.getpixel((0, 0)) == 0


def test_draw_rounded_rectangle_fill_and_outline() -> None:
    image = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    pillow_service.draw_rounded_rectangle(
        draw,
        (5, 5, 35, 35),
        radius=8,
        fill=(10, 20, 30, 255),
        outline=(1, 2, 3, 255),
        width=2,
    )
    assert image.getpixel((20, 20))[3] == 255


def test_get_frames_static_image() -> None:
    buf = io.BytesIO()
    _rgba((8, 8)).save(buf, format="PNG")
    buf.seek(0)

    frames, duration, is_animated = pillow_service.get_frames(buf)

    assert len(frames) == 1
    assert frames[0].mode == "RGBA"
    assert duration == 100
    assert is_animated is False


def test_get_frames_invalid_data() -> None:
    frames, duration, is_animated = pillow_service.get_frames(io.BytesIO(b"not-an-image"))
    assert frames == []
    assert duration == 0
    assert is_animated is False


def test_normalize_frame_count_with_extras() -> None:
    bg = [_rgba() for _ in range(3)]
    avatar = [_rgba() for _ in range(5)]
    extra = [_rgba() for _ in range(7)]
    assert pillow_service._normalize_frame_count(bg, avatar, [extra]) == 7


def test_extend_and_trim_repeats_and_truncates() -> None:
    frames = [_rgba()]
    extended = pillow_service._extend_and_trim(frames, 4)
    assert len(extended) == 4

    many = [_rgba() for _ in range(6)]
    trimmed = pillow_service._extend_and_trim(many, 3)
    assert len(trimmed) == 3


def test_create_overlay() -> None:
    overlay = pillow_service.create_overlay((12, 12), (1, 2, 3, 128))
    assert overlay.size == (12, 12)
    assert overlay.getpixel((0, 0)) == (1, 2, 3, 128)


def test_frame_for_palette_quantize_modes() -> None:
    rgb = pillow_service._frame_for_palette_quantize(_rgba().convert("RGB"))
    assert rgb.mode == "RGB"

    rgba = pillow_service._frame_for_palette_quantize(_rgba())
    assert rgba.mode == "RGB"

    gray = pillow_service._frame_for_palette_quantize(Image.new("L", (4, 4), 128))
    assert gray.mode == "L"


def test_quantize_frames_single_frame_unchanged() -> None:
    frames = [_rgba()]
    assert pillow_service._quantize_frames(frames) == frames


def test_save_optimized_gif_empty() -> None:
    buf = pillow_service.save_optimized_gif([], duration=100)
    assert buf.tell() == 0


def test_save_optimized_gif_single_frame() -> None:
    buf = pillow_service.save_optimized_gif([_rgba((16, 16))], duration=50, quantize=False)
    buf.seek(0)
    image = Image.open(buf)
    assert image.format == "GIF"


def test_process_frames_with_mask() -> None:
    background = _rgba((30, 30), (0, 0, 0, 0))
    avatar = _rgba((10, 10))
    mask = pillow_service.create_circular_mask((10, 10))
    result = pillow_service.process_frames_with_mask([background], mask, [(avatar, (5, 5))])
    assert len(result) == 1
    assert result[0].size == (30, 30)


@pytest.mark.asyncio
async def test_fetch_image_non_200() -> None:
    response = AsyncMock()
    response.status = 404
    response.read = AsyncMock(return_value=b"")
    session = MagicMock()
    session.get = MagicMock(return_value=AsyncMock(__aenter__=AsyncMock(return_value=response), __aexit__=AsyncMock()))
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=session)
    client.__aexit__ = AsyncMock(return_value=None)

    with patch("services.pillow_service.aiohttp.ClientSession", return_value=client):
        assert await pillow_service.fetch_image("https://example.test/missing.png") is None


@pytest.mark.asyncio
async def test_get_image_or_gif_frames_fetch_failure() -> None:
    with patch("services.pillow_service.fetch_image", new=AsyncMock(return_value=None)):
        frames, duration = await pillow_service.get_image_or_gif_frames("https://example.test/x.png")
    assert frames == []
    assert duration == 0


@pytest.mark.asyncio
async def test_run_in_executor() -> None:
    with patch("services.pillow_service._PILLOW_SERVICE_EXECUTOR") as executor:
        executor.submit = MagicMock()
        loop = MagicMock()
        loop.run_in_executor = AsyncMock(return_value=42)
        with patch("asyncio.get_event_loop", return_value=loop):
            result = await pillow_service.run_in_executor(sum, [1, 2, 3])
    assert result == 42
