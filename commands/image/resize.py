import io
from io import BytesIO

import discord
from PIL import Image

import utility
from localizer import tanjunLocalizer


async def resize(commandInfo: utility.commandInfo, image: discord.Attachment, width: int, height: int):
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
    image = image.resize((width, height))

    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.image.resize.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.image.resize.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await commandInfo.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
