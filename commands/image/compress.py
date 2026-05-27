import io
from io import BytesIO

import discord
from PIL import Image

import utility
from localizer import tanjunLocalizer


async def compress(command_info: utility.CommandInfo, image: discord.Attachment, quality: int):  # type: ignore[no-untyped-def]
    if isinstance(image, discord.Attachment) and not image.filename.endswith((".png", ".jpg", ".jpeg")):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.typenotsupported.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.typenotsupported.description"),
        )
        await command_info.reply(embed=embed)
        return

    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.filesize.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.filesize.description"),
        )
        await command_info.reply(embed=embed)
        return

    image = await image.read()  # type: ignore[assignment]
    image = Image.open(io.BytesIO(image))  # type: ignore[assignment, arg-type]

    # Convert to RGB mode (required for JPEG)
    if image.mode in ("RGBA", "P"):  # type: ignore[attr-defined]
        image = image.convert("RGB")  # type: ignore[attr-defined]

    buffer = BytesIO()
    # Save as JPEG with the specified quality
    image.save(buffer, format="JPEG", quality=quality, optimize=True)  # type: ignore[call-arg, unused-coroutine]
    buffer.seek(0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.compress.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.image.compress.success.description",
            newSize=f"{round(buffer.getbuffer().nbytes / 1024, 2)}",
            oldSize=f"{round(len(image.tobytes()) / 1024, 2)}",  # type: ignore[attr-defined]
        ),
    )
    embed.set_image(url="attachment://image.jpg")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.jpg"))
