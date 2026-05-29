"""Image filter helpers — consolidated via ImageService.

Individual command wrappers are re-exported from this module for backwards
compatibility. All actual processing lives in services/image_service.py.
"""

from __future__ import annotations

import io

import discord

from localizer import tanjunLocalizer
from services.image_service import ImageFilter, ImageOperation, ImageService
from utility import CommandInfo, tanjunEmbed

__all__ = [
    "ImageFilter",
    "ImageOperation",
    "ImageService",
    "apply_filter",
    "contour",
    "detail",
    "edge_enhance",
    "emboss",
    "find_edges",
    "sharpen",
    "smooth",
    # Non-filter operations kept for backward import compat
]

# ── Shared validation/response helper ────────────────────────────────────────


async def _validate_and_process(
    command_info: CommandInfo,
    image: discord.Attachment,
    operation: ImageOperation,
    *,
    locale_prefix: str = "image",
    success_locale_prefix: str | None = None,
) -> None:
    """Validate an image attachment, process it, and send the result as an embed.

    Parameters
    ----------
    command_info
    image
    operation
    locale_prefix : str
        Prefix for error locale keys (e.g. "image" or "image.blur").
    success_locale_prefix : str | None
        Prefix for success locale keys. Falls back to the operation filter name
        or "image.{operation_name}".
    """
    error = ImageService.validate_attachment(image)
    if error is not None:
        embed = ImageService.format_error_embed(
            str(command_info.locale),
            error,
            locale_prefix=locale_prefix,
        )
        await command_info.reply(embed=embed)
        return

    image_bytes = await image.read()
    result_bytes = await ImageService.process(image_bytes, operation)

    # Determine locale key for success message
    success_prefix = success_locale_prefix
    if success_prefix is None and operation.filter_name is not None:
        success_prefix = f"image.{operation.filter_name.value}"

    if operation.compress_quality is not None:
        disk_filename = "image.jpg"
        # Compute old size from the original image bytes
        old_size_kb = round(len(image_bytes) / 1024, 2)
        new_size_kb = round(len(result_bytes) / 1024, 2)

        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.compress.success.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.compress.success.description",
                newSize=f"{new_size_kb}",
                oldSize=f"{old_size_kb}",
            ),
        )
    elif operation.mirror_axis is not None or operation.resize is not None:
        disk_filename = "image.png"
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.resize.success.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.resize.success.description",
            ),
        )
    elif operation.scale is not None:
        disk_filename = "image.png"
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.rescale.success.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.rescale.success.description",
            ),
        )
    elif operation.remove_background:
        disk_filename = "image.png"
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.background.disabled.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.background.disabled.description",
            ),
        )
    else:
        disk_filename = "image.png"
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                f"commands.{success_prefix}.success.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                f"commands.{success_prefix}.success.description",
            ),
        )

    embed.set_image(url=f"attachment://{disk_filename}")
    await command_info.reply(
        embed=embed,
        file=discord.File(io.BytesIO(result_bytes), filename=disk_filename),
    )


# ── Public filter wrappers (used by extensions/image.py) ─────────────────────


async def apply_filter(
    command_info: CommandInfo,
    image: discord.Attachment,
    filter_name: str,
    *,
    error_locale_key: str = "image",
    success_locale_key: str | None = None,
    radius: int = 3,
) -> None:
    """Apply a PIL filter by name.

    This is the legacy API used by the blur command and simple filters.
    """
    try:
        resolved = ImageFilter(filter_name)
    except ValueError:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.error.unknown_filter.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.image.error.unknown_filter.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    operation = ImageOperation(filter_name=resolved, radius=radius)
    locale_prefix = error_locale_key
    success_prefix = success_locale_key

    error = ImageService.validate_attachment(image)
    if error is not None:
        embed = ImageService.format_error_embed(
            str(command_info.locale),
            error,
            locale_prefix=locale_prefix,
        )
        await command_info.reply(embed=embed)
        return

    image_bytes = await image.read()
    result_bytes = await ImageService.process(image_bytes, operation)

    if success_prefix is None:
        success_prefix = f"image.{resolved.value}"

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            str(command_info.locale),
            f"commands.{success_prefix}.success.title",
        ),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            f"commands.{success_prefix}.success.description",
        ),
    )
    embed.set_image(url="attachment://image.png")
    await command_info.reply(
        embed=embed,
        file=discord.File(io.BytesIO(result_bytes), filename="image.png"),
    )


async def contour(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply contour filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.CONTOUR),
        success_locale_prefix="image.contour",
    )


async def detail(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply detail filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.DETAIL),
        success_locale_prefix="image.detail",
    )


async def edge_enhance(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply edge enhance filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.EDGE_ENHANCE),
        success_locale_prefix="image.edgeenhance",
    )


async def emboss(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply emboss filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.EMBOSS),
        success_locale_prefix="image.emboss",
    )


async def find_edges(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply find edges filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.FIND_EDGES),
        success_locale_prefix="image.findedges",
    )


async def sharpen(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply sharpen filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.SHARPEN),
        success_locale_prefix="image.sharpen",
    )


async def smooth(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Apply smooth filter."""
    await _validate_and_process(
        command_info,
        image,
        ImageOperation(filter_name=ImageFilter.SMOOTH),
        success_locale_prefix="image.smooth",
    )
