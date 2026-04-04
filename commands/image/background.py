import io
from io import BytesIO

import discord  # type: ignore[import-not-found]
from PIL import Image
from rembg import remove as removeBackground  # type: ignore[import-not-found]

import utility
from localizer import tanjunLocalizer


async def background(commandInfo: utility.CommandInfo, image: discord.Attachment):  # type: ignore[no-any-unimported,no-untyped-def]
    if isinstance(image, discord.Attachment):
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.typenotsupported.title"),
                description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.typenotsupported.description"),
            )
            await commandInfo.reply(embed=embed)
            return

    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.filesize.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.filesize.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    image = await image.read()
    image = Image.open(io.BytesIO(image))
    image = removeBackground(image)

    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.background.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.background.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await commandInfo.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
