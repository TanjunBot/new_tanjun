import io
from io import BytesIO

import discord
from PIL import Image, ImageFilter

import utility
from localizer import tanjunLocalizer

# Map of filter names to PIL ImageFilter constructors
FILTERS = {
    "contour": lambda: ImageFilter.CONTOUR(),
    "detail": lambda: ImageFilter.DETAIL(),
    "edge_enhance": lambda: ImageFilter.EDGE_ENHANCE(),
    "emboss": lambda: ImageFilter.EMBOSS(),
    "find_edges": lambda: ImageFilter.FIND_EDGES(),
    "sharpen": lambda: ImageFilter.SHARPEN(),
    "smooth": lambda: ImageFilter.SMOOTH(),
    "gaussian_blur": lambda radius=3: ImageFilter.GaussianBlur(radius),
    "box_blur": lambda radius=3: ImageFilter.BoxBlur(radius),
}


async def apply_filter(
    commandInfo: utility.CommandInfo,
    image: discord.Attachment,
    filter_name: str,
    *,
    error_locale_key: str = "image",
    success_locale_key: str | None = None,
    radius: int = 3,
) -> None:
    """Apply a PIL filter to an image and send the result.

    Parameters
    ----------
    commandInfo
    image : discord.Attachment
    filter_name : str
        Key into FILTERS dict.
    error_locale_key : str
        Localization key prefix for type/filesize errors.
        For simple filters: "image" (resolves to commands.image.typenotsupported.*)
        For blur: "image.blur" (resolves to commands.image.blur.typenotsupported.*)
    success_locale_key : str | None
        Localization key prefix for success message.
        Defaults to f"image.{filter_name}" for simple filters.
    radius : int
        Radius for blur filters. Ignored for non-blur filters.
    """
    success_key = success_locale_key or f"image.{filter_name}"

    if isinstance(image, discord.Attachment):
        if not image.filename.endswith((".png", ".jpg", ".jpeg")):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), f"commands.{error_locale_key}.typenotsupported.title"),
                description=tanjunLocalizer.localize(
                    str(commandInfo.locale), f"commands.{error_locale_key}.typenotsupported.description"
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    if image.size > 8 * 1024 * 1024:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), f"commands.{error_locale_key}.filesize.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), f"commands.{error_locale_key}.filesize.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    image_data = await image.read()
    pil_image = Image.open(io.BytesIO(image_data))

    if filter_name in ("gaussian_blur", "box_blur"):
        pil_image = pil_image.filter(FILTERS[filter_name](radius))
    else:
        filter_func = FILTERS.get(filter_name)
        if filter_func is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.error.unknown_filter.title"),
                description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.image.error.unknown_filter.description"),
            )
            await commandInfo.reply(embed=embed)
            return
        pil_image = pil_image.filter(filter_func())

    buffer = BytesIO()
    pil_image.save(buffer, format="png")
    buffer.seek(0)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"commands.{success_key}.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), f"commands.{success_key}.success.description"),
    )
    embed.set_image(url="attachment://image.png")
    await commandInfo.reply(embed=embed, file=discord.File(fp=buffer, filename="image.png"))
