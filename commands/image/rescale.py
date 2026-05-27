import io
from io import BytesIO

import discord
from PIL import Image

import utility
from localizer import tanjunLocalizer


async def rescale(command_info: utility.CommandInfo, image: discord.Attachment, factor: float):  # type: ignore[no-untyped-def]
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
    image = image.resize((int(image.width * factor), int(image.height * factor)))  # type: ignore[attr-defined, operator]

    buffer = BytesIO()
    image.save(buffer, format="png")  # type: ignore[call-arg, unused-coroutine]
    buffer.seek(0)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.image.rescale.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.image.rescale.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await command_info.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
