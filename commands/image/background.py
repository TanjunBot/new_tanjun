"""Background removal command — thin wrapper around ImageService.

Background removal is currently disabled (rembg not available).
Returns the original image with a 'disabled' message.
"""

from __future__ import annotations

import discord

from services.image_service import ImageOperation, ImageService
from utility import CommandInfo


async def background(command_info: CommandInfo, image: discord.Attachment) -> None:
    """Remove image background (currently disabled — returns original)."""
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
    result_bytes = await ImageService.process(image_bytes, ImageOperation(remove_background=True))

    from io import BytesIO  # noqa: PLC0415

    import utility  # noqa: PLC0415
    from localizer import tanjunLocalizer  # noqa: PLC0415

    buffer = BytesIO(result_bytes)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.background.disabled.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.background.disabled.description"),
    )
    embed.set_image(url="attachment://image.png")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
