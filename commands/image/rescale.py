"""Image rescale command — thin wrapper around ImageService."""

from __future__ import annotations

import discord

from localizer import tanjunLocalizer
from services.image_service import ImageOperation, ImageService
from utility import CommandInfo, tanjunEmbed


async def rescale(command_info: CommandInfo, image: discord.Attachment, factor: float) -> None:
    """Rescale an image by a factor."""
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
    operation = ImageOperation(scale=factor)
    result_bytes = await ImageService.process(image_bytes, operation)

    from io import BytesIO  # noqa: PLC0415

    buffer = BytesIO(result_bytes)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.rescale.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.rescale.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
