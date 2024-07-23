import utility
from localizer import tanjunLocalizer
import discord
from PIL import Image, ImageFilter
import io
from io import BytesIO


async def blur_image(commandInfo: utility.commandInfo, image: discord.Attachment, type: str = "gaussian", radius: int = 3):
    if isinstance(image, discord.Attachment):
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            embed = utility.tanjunEmbed(
                title = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.typenotsupported.title"),
                description = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.typenotsupported.description"),
            )
            await commandInfo.reply(embed=embed)
            return
        
    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.filesize.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.filesize.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    image = await image.read()
    image = Image.open(io.BytesIO(image))
    if type == "gaussian":
        image = image.filter(ImageFilter.GaussianBlur(radius))
    elif type == "boxblurr":
        image = image.filter(ImageFilter.BoxBlur(radius))

    buffer = BytesIO()
    image.save(buffer, format="png")
    buffer.seek(0)
    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.success.title"),
        description = tanjunLocalizer.localize(commandInfo.locale, "commands.image.blur.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await commandInfo.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))