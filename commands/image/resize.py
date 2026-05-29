"""Image resize command — thin wrapper around ImageService."""

from __future__ import annotations

import discord

from localizer import tanjunLocalizer
from services.image_service import ImageOperation, ImageService
from utility import CommandInfo, tanjunEmbed


async def resize(command_info: CommandInfo, image: discord.Attachment, width: int, height: int) -> None:
    """Resize an image to exact dimensions."""
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
    operation = ImageOperation(resize=(width, height))
    result_bytes = await ImageService.process(image_bytes, operation)

    from io import BytesIO  # noqa: PLC0415

    buffer = BytesIO(result_bytes)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.resize.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.resize.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
