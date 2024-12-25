import utility
from localizer import tanjunLocalizer
import discord
from PIL import Image
import io
from io import BytesIO


async def rescale(
    commandInfo: utility.commandInfo, image: discord.Attachment, factor: float
):
    if isinstance(image, discord.Attachment):
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.image.typenotsupported.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.image.typenotsupported.description"
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.image.filesize.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.image.filesize.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    image = await image.read()
    image = Image.open(io.BytesIO(image))
    image = image.resize((int(image.width * factor), int(image.height * factor)))

    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.image.rescale.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.image.rescale.success.description"
        ),
    )
    embed.set_image(url="attachment://image.png")
    await commandInfo.reply(
        embed=embed, file=discord.File(fp=buffer, filename="image.png")
    )
