"""Image compress command — thin wrapper around ImageService."""

from __future__ import annotations

import discord

from services.image_service import ImageOperation, ImageService
from utility import CommandInfo


async def compress(command_info: CommandInfo, image: discord.Attachment, quality: int) -> None:
    """Compress an image by re-encoding as JPEG at the given quality level."""
    error = ImageService.validate_attachment(image)
    if error is not None:
        embed = ImageService.format_error_embed(
            str(command_info.locale),
            error,
            locale_prefix="image",
        )
        await command_info.reply(embed=embed)
        return

    image_bytes = await image.read()
    operation = ImageOperation(compress_quality=quality)
    result_bytes = await ImageService.process(image_bytes, operation)

    from io import BytesIO  # noqa: PLC0415

    import utility  # noqa: PLC0415
    from localizer import tanjunLocalizer  # noqa: PLC0415

    orig_size_kb = round(len(image_bytes) / 1024, 2)
    new_size_kb = round(len(result_bytes) / 1024, 2)

    buffer = BytesIO(result_bytes)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.compress.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.image.compress.success.description",
            newSize=f"{new_size_kb}",
            oldSize=f"{orig_size_kb}",
        ),
    )
    embed.set_image(url="attachment://image.jpg")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.jpg"))
