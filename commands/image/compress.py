import io
from io import BytesIO

import discord
from PIL import Image

import utility
from localizer import tanjunLocalizer


async def compress(commandInfo: utility.commandInfo, image: discord.Attachment, quality: int):
    if isinstance(image, discord.Attachment):
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.image.typenotsupported.title"),
                description=tanjunLocalizer.localize(commandInfo.locale, "commands.image.typenotsupported.description"),
            )
            await commandInfo.reply(embed=embed)
            return

    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.image.filesize.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.image.filesize.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    image = await image.read()
    image = Image.open(io.BytesIO(image))

    # Convert to RGB mode (required for JPEG)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    buffer = BytesIO()
    # Save as JPEG with the specified quality
    image.save(buffer, format="JPEG", quality=quality, optimize=True)
    buffer.seek(0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.image.compress.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.image.compress.success.description",
            newSize=f"{round(buffer.getbuffer().nbytes / 1024, 2)}",
            oldSize=f"{round(len(image.tobytes()) / 1024, 2)}",
        ),
    )
    embed.set_image(url="attachment://image.jpg")
    await commandInfo.reply(embed=embed, file=discord.File(fp=buffer, filename="image.jpg"))
