import io
from typing import Any

import discord
from PIL import Image, ImageDraw

from api import get_user_level_info, set_custom_background
from localizer import tanjunLocalizer
from models import UserLevelInfoModel
from services.pillow_service import (
    create_circular_mask,
    create_overlay,
    draw_rounded_rectangle,
    fetch_image,
    get_image_or_gif_frames,
    load_font,
    run_in_executor,
    save_optimized_gif,
)
from utility import CommandInfo, draw_text_with_outline, tanjunEmbed, upload_image_to_imgbb


async def show_rankcard_command(command_info: CommandInfo, user: discord.Member) -> None:
    assert command_info.guild is not None
    user_info = await get_user_level_info(str(command_info.guild.id), str(user.id))

    if not user_info:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.rank.error.no_data.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.rank.error.no_data.description",
                user=user.mention,
            ),
        )
        await command_info.reply(embed=embed)
        return

    rankcard_image = await generate_rankcard(user, user_info, command_info)

    file = discord.File(rankcard_image, filename="rankcard.gif")
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.rank.success.title", user=user.name),
    )
    embed.set_image(url="attachment://rankcard.gif")

    await command_info.reply(embed=embed, file=file)


async def set_background_command(command_info: CommandInfo, image: discord.Attachment) -> None:
    if image.content_type not in ["image/png", "image/jpeg", "image/gif"]:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.setbackground.error.invalid_format.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.setbackground.error.invalid_format.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    uploaded_image = await upload_image_to_imgbb(await image.read(), image.content_type.split("/")[1])

    await set_custom_background(
        str(command_info.guild.id),  # type: ignore[union-attr]
        str(command_info.user.id),
        uploaded_image["data"]["url"],  # type: ignore[index]
    )

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.setbackground.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.level.setbackground.success.description"),
    )
    embed.set_image(url=uploaded_image["data"]["url"])  # type: ignore[index]

    await command_info.reply(embed=embed)


async def generate_rankcard(user: discord.Member, user_info: dict[str, Any], command_info: CommandInfo) -> io.BytesIO:
    # Load background image or frames
    custom_bg = user_info.custom_background
    if custom_bg:
        background_frames, _ = await get_image_or_gif_frames(str(custom_bg))
    else:
        background_frames = [Image.open("assets/rankCard.png").convert("RGBA")]

    # Load user avatar frames
    avatar_url = str(user.display_avatar.url)
    avatar_frames, _ = await get_image_or_gif_frames(avatar_url)
    avatar_decoration_frames: list[Image.Image] | None = None
    avatar_decoration_url = str(user.avatar_decoration.url) if user.avatar_decoration else None
    if avatar_decoration_url:
        avatar_decoration_frames, _ = await get_image_or_gif_frames(avatar_decoration_url)

    # Process image in executor
    img_byte_arr = await run_in_executor(
        _process_image_sync,
        background_frames,
        avatar_frames,
        avatar_decoration_frames,
        user,
        user_info,
        command_info,
    )

    if not isinstance(img_byte_arr, io.BytesIO):
        raise TypeError("Expected io.BytesIO from _process_image_sync")

    return img_byte_arr


def _process_image_sync(
    background_frames: list[Image.Image],
    avatar_frames: list[Image.Image],
    avatar_decoration_frames: list[Image.Image] | None,
    user: discord.Member,
    user_info: UserLevelInfoModel,
    command_info: CommandInfo,
) -> io.BytesIO:
    decoration_size_multiplier = 1.2

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
        decoration_size = int(200 * decoration_size_multiplier)
        offset = int((decoration_size - 200) / 2)
        for i in range(len(avatar_decoration_frames)):
            avatar_decoration_frames[i] = avatar_decoration_frames[i].resize((decoration_size, decoration_size))

    mask = create_circular_mask((200, 200))

    result_frames: list[Image.Image] = []

    for frame_index in range(num_frames):
        bg_frame = background_frames[frame_index]
        frame = bg_frame.copy()

        # Draw a semi-transparent black rectangle over the background
        overlay = create_overlay(frame.size, (0, 0, 0, 100))
        frame = Image.alpha_composite(frame, overlay)

        username_font = load_font("assets/fonts/Arial.ttf", 40)
        info_font = load_font("assets/fonts/Arial.ttf", 30)

        draw = ImageDraw.Draw(frame)

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
            tanjunLocalizer.localize(str(command_info.locale), "commands.level.rank.data.level", level=user_info.level),
            info_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )
        draw_text_with_outline(
            draw,
            (250, 150),
            tanjunLocalizer.localize(
                command_info.locale,
                "commands.level.rank.data.xp",
                xp=user_info.xp,
                xp_needed=user_info.xp_needed,
            ),
            info_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )

        bar_width = 700
        bar_height = 30
        xp_percentage = user_info.xp / (user_info.xp_needed if user_info.xp_needed > 0 else 1)
        filled_width = int(bar_width * xp_percentage)
        radius = bar_height // 4

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
            decoration = decoration.resize((decoration_size, decoration_size)).convert("RGBA")  # type: ignore[possibly-undefined]
            decoration_layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
            decoration_layer.paste(decoration, (25 - offset, 50 - offset), decoration)  # type: ignore[possibly-undefined]
            frame = Image.alpha_composite(frame, decoration_layer)

        result_frames.append(frame)

    duration = int(background_frames[0].info.get("duration", 100))
    return save_optimized_gif(result_frames, duration)
