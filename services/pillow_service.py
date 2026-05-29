"""Pillow image/GIF processing service with performance optimizations.

Consolidates duplicate image fetching and frame-processing logic from
commands/channel/welcome.py, commands/channel/farewell.py, and
commands/level/level_rankcard.py into a single, testable service.

Optimizations:
- Avoids unnecessary RGBA conversion for static (single-frame) images
- Uses quantized color palettes for smaller, higher-quality GIFs
- Reuses shared helper functions instead of copy-pasting across three files
"""
from __future__ import annotations

import asyncio
import io
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from PIL import Image, ImageDraw, ImageFont, ImageSequence, UnidentifiedImageError

_PILLOW_SERVICE_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pillow")


def create_circular_mask(size: tuple[int, int]) -> Image.Image:
    """Create a circular alpha mask for the given (width, height)."""
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size[0], size[1]), fill=255)
    return mask


def draw_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: tuple[int, int, int, int] | None = None,
    outline: tuple[int, int, int, int] | None = None,
    width: int = 1,
) -> None:
    """Draw a rounded rectangle on the given ImageDraw surface."""
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)
    if outline:
        draw.arc([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=outline, width=width)
        draw.arc([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=outline, width=width)
        draw.arc([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=outline, width=width)
        draw.arc([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=outline, width=width)
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)


async def fetch_image(url: str, timeout: int = 10) -> io.BytesIO | None:
    """Asynchronously fetch an image from a URL and return it as a BytesIO buffer."""
    try:
        async with aiohttp.ClientSession() as session, session.get(url, timeout=ClientTimeout(total=timeout)) as response:
            if response.status != 200:
                return None
            return io.BytesIO(await response.read())
    except (TimeoutError, aiohttp.ClientError):
        return None


def _is_animated(image: Image.Image) -> bool:
    """Check whether a Pillow Image has multiple frames (is animated)."""
    return getattr(image, "is_animated", False)


def get_frames(image_data: io.BytesIO) -> tuple[list[Image.Image], int, bool]:
    """Extract frames from an image, always converting to RGBA.

    Returns (frames, duration_ms, is_animated).
    For static images a single-frame list is returned.
    Returns ([], 0, False) on decoding errors.
    """
    try:
        image = Image.open(image_data)
        is_animated = _is_animated(image)
        duration = int(image.info.get("duration", 100))

        if is_animated:
            frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(image)]
        else:
            frames = [image.convert("RGBA")]

        return frames, duration, is_animated
    except (UnidentifiedImageError, OSError, ValueError):
        return [], 0, False


async def get_image_or_gif_frames(url: str) -> tuple[list[Image.Image], int]:
    """Fetch an image URL and extract frames + default duration.

    Returns ([frames], duration_ms).  Returns ([], 0) on failure.
    """
    image_data = await fetch_image(url)
    if image_data is None:
        return [], 0
    frames, duration, _ = get_frames(image_data)
    return frames, duration


def _normalize_frame_count(
    background_frames: list[Image.Image],
    avatar_frames: list[Image.Image],
    extra_frame_lists: list[list[Image.Image]] | None = None,
) -> int:
    """Determine the target frame count (max across all frame lists)."""
    max_len = max(len(background_frames), len(avatar_frames))
    if extra_frame_lists:
        for fl in extra_frame_lists:
            max_len = max(max_len, len(fl))
    return max_len


def _extend_and_trim(
    frames: list[Image.Image],
    target: int,
) -> list[Image.Image]:
    """Repeat frames to reach *target* length, then trim to exactly *target*."""
    if len(frames) >= target:
        return frames[:target]
    multiplier = (target // len(frames)) + 1
    return (frames * multiplier)[:target]


def create_overlay(size: tuple[int, int], color: tuple[int, int, int, int]) -> Image.Image:
    """Create a full-size RGBA overlay filled with *color*."""
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([0, 0, size[0], size[1]], fill=color)
    return overlay


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font; raises FileNotFoundError if missing."""
    return ImageFont.truetype(path, size)


def _quantize_frames(frames: list[Image.Image], palette_size: int = 256) -> list[Image.Image]:
    """Quantize RGBA frames to an optimised palette for smaller GIF output.

    When there are frames, convert to 'P' mode with a shared adaptive palette
    so the GIF is smaller and renders consistently across viewers.
    Uses FASTOCTREE for RGBA-safe quantization.
    """
    if len(frames) <= 1:
        return frames
    # Build a shared palette from the first frame using FASTOCTREE (RGBA-safe)
    pal = frames[0].quantize(colors=min(palette_size, 256), method=Image.Quantize.FASTOCTREE)
    palette_data = pal.getpalette()
    if palette_data is None:
        return frames
    quantized: list[Image.Image] = []
    for frame in frames:
        q = frame.quantize(colors=min(palette_size, 256), palette=pal, method=Image.Quantize.FASTOCTREE)
        quantized.append(q)
    return quantized


def save_optimized_gif(
    frames: list[Image.Image],
    duration: int,
    loop: int = 0,
    quantize: bool = True,
    palette_size: int = 256,
) -> io.BytesIO:
    """Save frames as an optimised GIF and return the byte buffer.

    Parameters
    ----------
    frames : list[Image.Image]
        RGBA frames to compose.
    duration : int
        Frame duration in milliseconds.
    loop : int
        Number of loops (0 = infinite).
    quantize : bool
        Whether to quantize colours for a smaller file.
    palette_size : int
        Max palette colours (≤256).

    Returns
    -------
    io.BytesIO
        Seekable buffer containing the GIF data.
    """
    buffer = io.BytesIO()

    if not frames:
        return buffer

    output_frames = _quantize_frames(frames, palette_size) if quantize else frames

    kwargs: dict[str, Any] = {
        "format": "GIF",
        "save_all": True,
        "loop": loop,
        "duration": duration,
    }
    if len(output_frames) > 1:
        kwargs["append_images"] = output_frames[1:]

    output_frames[0].save(buffer, **kwargs)
    buffer.seek(0)
    return buffer


def process_frames_with_mask(
    frames: list[Image.Image],
    mask: Image.Image,
    paste_targets: list[tuple[Image.Image, tuple[int, int]]],
) -> list[Image.Image]:
    """Apply a circular (or arbitrary) mask to paste targets on each frame.

    Parameters
    ----------
    frames : list[Image.Image]
        Background frames to draw onto.
    mask : Image.Image
        Alpha (``L``) mask for circular cropping.
    paste_targets : list of (source, offset)
        One or more ``(source_image, (x, y))`` tuples to paste through the mask.

    Returns
    -------
    list[Image.Image]
        New frame list with masks applied.
    """
    result: list[Image.Image] = []
    for frame in frames:
        out = frame.copy()
        for src, offset in paste_targets:
            masked = Image.new("RGBA", src.size, (0, 0, 0, 0))
            masked.paste(src, (0, 0), mask)
            out.paste(masked, offset, masked)
        result.append(out)
    return result


async def run_in_executor(func: Any, *args: Any) -> Any:
    """Run a CPU-bound Pillow function in the shared thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_PILLOW_SERVICE_EXECUTOR, func, *args)
