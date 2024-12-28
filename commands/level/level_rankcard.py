import discord
from utility import commandInfo, tanjunEmbed, checkIfhasPlus, draw_text_with_outline
from localizer import tanjunLocalizer
from api import get_user_level_info, set_custom_background
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import io
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from utility import upload_image_to_imgbb

executor = ThreadPoolExecutor()


async def show_rankcard_command(commandInfo: commandInfo, user: discord.Member):
    user_info = await get_user_level_info(str(commandInfo.guild.id), str(user.id))

    if not user_info:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.rank.error.no_data.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.rank.error.no_data.description",
                user=user.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    rankcard_image = await generate_rankcard(user, user_info)

    file = discord.File(rankcard_image, filename="rankcard.gif")
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.rank.success.title", user=user.name
        ),
    )
    embed.set_image(url="attachment://rankcard.gif")

    await commandInfo.reply(embed=embed, file=file)


async def set_background_command(commandInfo: commandInfo, image: discord.Attachment):
    if not checkIfhasPlus(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setbackground.error.no_plus.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setbackground.error.no_plus.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if image.content_type not in ["image/png", "image/jpeg", "image/gif"]:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setbackground.error.invalid_format.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setbackground.error.invalid_format.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    uploaded_image = await upload_image_to_imgbb(
        await image.read(), image.content_type.split("/")[1]
    )

    await set_custom_background(
        str(commandInfo.guild.id),
        str(commandInfo.user.id),
        uploaded_image["data"]["url"],
    )

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.setbackground.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.setbackground.success.description"
        ),
    )
    embed.set_image(url=uploaded_image["data"]["url"])

    await commandInfo.reply(embed=embed)


async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None
            image_data = io.BytesIO(await response.read())
            return image_data


async def get_image_or_gif_frames(url):
    image_data = await fetch_image(url)
    image = Image.open(image_data)
    frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(image)]
    duration = image.info.get("duration", 100)
    return frames, duration


def draw_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill)
    if outline:
        draw.arc(
            [x1, y1, x1 + 2 * radius, y1 + 2 * radius],
            180,
            270,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x2 - 2 * radius, y1, x2, y1 + 2 * radius],
            270,
            360,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x1, y2 - 2 * radius, x1 + 2 * radius, y2],
            90,
            180,
            fill=outline,
            width=width,
        )
        draw.arc(
            [x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=outline, width=width
        )
        draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
        draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
        draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
        draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)


def process_image(
    background_frames, avatar_frames, avatar_decoration_frames, user, user_info
):
    DECORATION_SIZE_MULTIPLIER = 1.2

    num_frames = max(
        len(background_frames),
        len(avatar_frames),
        len(avatar_decoration_frames) if avatar_decoration_frames else 0,
    )

    # Extend frames to match the longest animation
    background_frames *= (num_frames // len(background_frames)) + 1
    avatar_frames *= (num_frames // len(avatar_frames)) + 1
    if avatar_decoration_frames:
        avatar_decoration_frames *= (num_frames // len(avatar_decoration_frames)) + 1

    # Trim excess frames
    background_frames = background_frames[:num_frames]
    avatar_frames = avatar_frames[:num_frames]
    if avatar_decoration_frames:
        avatar_decoration_frames = avatar_decoration_frames[:num_frames]

    for i in range(len(background_frames)):
        background_frames[i] = background_frames[i].resize((1000, 300))

    for i in range(len(avatar_frames)):
        avatar_frames[i] = avatar_frames[i].resize((200, 200))

    # Resize decoration frames if they exist
    if avatar_decoration_frames:
        decoration_size = int(200 * DECORATION_SIZE_MULTIPLIER)
        offset = int((decoration_size - 200) / 2)
        for i in range(len(avatar_decoration_frames)):
            avatar_decoration_frames[i] = avatar_decoration_frames[i].resize(
                (decoration_size, decoration_size)
            )

    mask = Image.new("L", (200, 200), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 200, 200), fill=255)

    result_frames = []

    for frame_index in range(num_frames):
        bg_frame = background_frames[frame_index]
        frame = bg_frame.copy()
        draw = ImageDraw.Draw(frame)

        # Draw a semi-transparent black rectangle over the background
        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([0, 0, 1000, 300], fill=(0, 0, 0, 100))
        frame = Image.alpha_composite(frame, overlay)

        username_font = ImageFont.truetype("assets/fonts/Arial.ttf", 40)
        info_font = ImageFont.truetype("assets/fonts/Arial.ttf", 30)

        draw = ImageDraw.Draw(frame)  # Redefine draw to work on the composite image

        draw_text_with_outline(
            draw,
            (250, 50),
            user.name,
            username_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )
        draw_text_with_outline(
            draw,
            (250, 105),
            f"Level: {user_info['level']}",
            info_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )
        draw_text_with_outline(
            draw,
            (250, 150),
            f"XP: {user_info['xp']}/{user_info['xp_needed']}",
            info_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )

        bar_width = 700
        bar_height = 30
        xp_percentage = user_info["xp"] / user_info["xp_needed"]
        filled_width = int(bar_width * xp_percentage)
        radius = bar_height // 4  # Slightly rounded corners

        # Background bar
        draw_rounded_rectangle(
            draw,
            [250, 200, 250 + bar_width, 200 + bar_height],
            radius,
            fill=(50, 50, 50, 200),
            outline=(255, 255, 255, 255),
            width=2,
        )
        # Filled bar
        if xp_percentage >= 0.02:
            draw_rounded_rectangle(
                draw,
                [250, 200, 250 + filled_width, 200 + bar_height],
                radius,
                fill=(127, 219, 255, 200),
                outline=(255, 255, 255, 200),
                width=2,
            )

        # Create avatar output with mask
        output = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        output.paste(avatar_frames[frame_index], (0, 0), mask)
        frame.paste(output, (25, 50), output)

        # Add decoration if it exists
        if avatar_decoration_frames:
            decoration = avatar_decoration_frames[frame_index]
            # Resize the decoration and ensure RGBA mode
            decoration = decoration.resize((decoration_size, decoration_size)).convert('RGBA')
            # Create a new transparent image for the decoration
            decoration_layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
            # Paste the decoration onto the transparent layer
            decoration_layer.paste(decoration, (25 - offset, 50 - offset), decoration)
            # Composite the decoration layer with the frame
            frame = Image.alpha_composite(frame, decoration_layer)

        result_frames.append(frame)

    img_byte_arr = io.BytesIO()
    result_frames[0].save(
        img_byte_arr,
        format="GIF",
        save_all=True,
        append_images=result_frames[1:],
        loop=0,
        duration=background_frames[0].info.get("duration", 100),
    )
    img_byte_arr.seek(0)

    return img_byte_arr


async def generate_rankcard(user: discord.Member, user_info: dict) -> io.BytesIO:
    # Load background image or frames
    if user_info["customBackground"]:
        background_frames, _ = await get_image_or_gif_frames(
            user_info["customBackground"]
        )
    else:
        background_frames = [Image.open("assets/rankCard.png").convert("RGBA")]

    # Load user avatar frames
    avatar_url = str(user.display_avatar.url)
    avatar_frames, _ = await get_image_or_gif_frames(avatar_url)

    avatar_decoration_url = (
        str(user.avatar_decoration.url) if user.avatar_decoration else None
    )
    if avatar_decoration_url:
        avatar_decoration_frames, _ = await get_image_or_gif_frames(
            avatar_decoration_url
        )

    # Process image in executor
    loop = asyncio.get_event_loop()
    img_byte_arr = await loop.run_in_executor(
        executor,
        process_image,
        background_frames,
        avatar_frames,
        avatar_decoration_frames,
        user,
        user_info,
    )

    return img_byte_arr
