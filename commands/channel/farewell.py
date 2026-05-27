from __future__ import annotations

import asyncio
import io
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import discord
from aiohttp import ClientTimeout
from PIL import Image, ImageDraw, ImageFont, ImageSequence

import utility
from api import (
    get_leave_channel,
    remove_leave_channel,
    set_leave_channel,
)
from localizer import tanjunLocalizer
from utility import checkIfHasPro, draw_text_with_outline

executor = ThreadPoolExecutor()


async def setFarewellChannel(
    commandInfo: utility.CommandInfo,
    channel: discord.TextChannel,
    message: str | None = None,
    image_background: discord.Attachment = None,  # type: ignore[assignment]
) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if (
        not channel.permissions_for(commandInfo.guild.me).send_messages  # type: ignore[union-attr]
        or not channel.permissions_for(commandInfo.guild.me).embed_links  # type: ignore[union-attr]
        or not channel.permissions_for(commandInfo.guild.me).attach_files  # type: ignore[union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingBotPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_leave_channel(commandInfo.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.alreadySet.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.alreadySet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if image_background and not checkIfHasPro(commandInfo.user):  # type: ignore[truthy-bool, arg-type]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPro.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    imgUrl = None

    if image_background is not None:
        imgUrl = (
            await utility.upload_image_to_imgbb(
                image_background, image_background.filename.split(".")[-1]
            )
        )["data"]["url"]
    else:
        imgUrl = "https://i.ibb.co/4ppwFGG/default-join-and-leave-background.png"  # type: ignore[unreachable]

    await set_leave_channel(commandInfo.guild.id, channel.id, message, imgUrl)  # type: ignore[union-attr, arg-type]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.farewell.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.farewell.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)


async def removeFarewellChannel(commandInfo: utility.CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.farewell.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await get_leave_channel(commandInfo.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.farewell.notSet.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.channel.farewell.notSet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_leave_channel(commandInfo.guild.id)  # type: ignore[union-attr]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.farewell.deleteSuccess.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.farewell.deleteSuccess.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def fetch_image(url: str) -> io.BytesIO | None:
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, timeout=ClientTimeout(total=10)) as response,
        ):
            if response.status != 200:
                return None
            image_data = io.BytesIO(await response.read())
            return image_data
    except (TimeoutError, aiohttp.ClientError):
        return None


async def get_image_or_gif_frames(url) -> None:  # type: ignore[no-untyped-def]
    image_data = await fetch_image(url)
    if image_data is None:
        return None
    image = Image.open(image_data)  # type: ignore[arg-type]
    frames = [frame.copy().convert("RGBA") for frame in ImageSequence.Iterator(image)]
    duration = image.info.get("duration", 100)
    return frames, duration  # type: ignore[return-value]


def process_image(background_frames, avatar_frames, user) -> None:  # type: ignore[no-untyped-def]
    num_frames = max(len(background_frames), len(avatar_frames))
    background_frames *= (num_frames // len(background_frames)) + 1
    avatar_frames *= (num_frames // len(avatar_frames)) + 1
    background_frames = background_frames[:num_frames]
    avatar_frames = avatar_frames[:num_frames]
    member_number_locale = tanjunLocalizer.localize(
        (user.guild.preferred_locale if hasattr(user.guild, "preferred_locale") else "en"),
        "commands.admin.channel.farewell.memberNumber",
        member_count=user.guild.member_count,
    )

    for i in range(len(background_frames)):
        background_frames[i] = background_frames[i].resize((600, 400))

    for i in range(len(avatar_frames)):
        avatar_frames[i] = avatar_frames[i].resize((150, 150))

    mask = Image.new("L", (150, 150), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 150, 150), fill=255)

    result_frames = []

    for frame_index in range(num_frames):
        bg_frame = background_frames[frame_index]
        avatar_frame = avatar_frames[frame_index]

        frame = bg_frame.copy()
        draw = ImageDraw.Draw(frame)

        overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle([0, 0, 600, 400], fill=(0, 0, 0, 100))
        frame = Image.alpha_composite(frame, overlay)

        username_font = ImageFont.truetype("assets/fonts/Arial.ttf", 36)
        info_font = ImageFont.truetype("assets/fonts/Arial.ttf", 24)

        draw = ImageDraw.Draw(frame)

        username_bbox = draw.textbbox((0, 0), user.name, font=username_font)
        username_width = username_bbox[2] - username_bbox[0]
        username_x = (600 - username_width) // 2

        member_bbox = draw.textbbox((0, 0), member_number_locale, font=info_font)
        member_width = member_bbox[2] - member_bbox[0]
        member_x = (600 - member_width) // 2

        draw_text_with_outline(
            draw,
            (username_x, 250),  # type: ignore[arg-type]
            user.name,
            username_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )

        draw_text_with_outline(
            draw,
            (member_x, 300),  # type: ignore[arg-type]
            member_number_locale,
            info_font,
            (255, 255, 255, 255),
            (0, 0, 0, 255),
        )

        output = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
        output.paste(avatar_frame, (0, 0), mask)
        avatar_x = (600 - 150) // 2
        frame.paste(output, (avatar_x, 70), output)

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

    return img_byte_arr  # type: ignore[return-value]


async def farewellUser(member: discord.Member) -> None:
    farewellChannel = await get_leave_channel(member.guild.id)
    if farewellChannel is None:
        return

    background_frames, _ = await get_image_or_gif_frames(farewellChannel.image_background)  # type: ignore[func-returns-value, misc, call-overload, name-defined]

    avatar_url = str(member.display_avatar.url)
    avatar_frames, _ = await get_image_or_gif_frames(avatar_url)  # type: ignore[func-returns-value, misc]

    loop = asyncio.get_event_loop()
    img_byte_arr = await loop.run_in_executor(  # type: ignore[func-returns-value]
        executor,
        process_image,
        background_frames,  # type: ignore[has-type]
        avatar_frames,  # type: ignore[has-type]
        member,
    )

    file = discord.File(img_byte_arr, filename="bg.gif")  # type: ignore[arg-type]

    description = farewellChannel.message

    if not description:
        description = tanjunLocalizer.localize(
            (member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en"),
            "commands.admin.channel.farewell.success.description",
        )

    description = description.replace("{user}", member.mention)
    description = description.replace("{guild}", member.guild.name)
    description = description.replace("{member}", str(member.guild.member_count))

    embed = utility.tanjunEmbed(
        description=description,
    )
    embed.set_image(url="attachment://bg.gif")

    channel = await member.guild.fetch_channel(int(farewellChannel.channel_id))

    await channel.send(embed=embed, file=file)  # type: ignore[union-attr]
