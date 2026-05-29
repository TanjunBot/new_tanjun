from __future__ import annotations

import io

import discord
from PIL import Image, ImageDraw

import utility
from api import (
    get_welcome_channel,
    remove_welcome_channel,
    set_welcome_channel,
)
from localizer import tanjunLocalizer
from services.pillow_service import (
    create_circular_mask,
    create_overlay,
    get_image_or_gif_frames,
    load_font,
    run_in_executor,
    save_optimized_gif,
)
from utility import draw_text_with_outline


async def setWelcomeChannel(
    command_info: utility.CommandInfo,
    channel: discord.TextChannel,
    message: str | None = None,
    image_background: discord.Attachment = None,  # type: ignore[assignment]
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        not channel.permissions_for(command_info.guild.me).send_messages  # type: ignore[union-attr]
        or not channel.permissions_for(command_info.guild.me).embed_links  # type: ignore[union-attr]
        or not channel.permissions_for(command_info.guild.me).attach_files  # type: ignore[union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingBotPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await get_welcome_channel(command_info.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.alreadySet.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.alreadySet.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    img_url = None

    if image_background is not None:
        img_url = (await utility.upload_image_to_imgbb(image_background, image_background.filename.split(".")[-1]))["data"][
            "url"
        ]
    else:
        img_url = "https://i.ibb.co/4ppwFGG/default-join-and-leave-background.png"  # type: ignore[unreachable]

    await set_welcome_channel(command_info.guild.id, channel.id, message, img_url)  # type: ignore[union-attr, arg-type]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.welcome.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.channel.welcome.success.description",
            channel=channel.mention,
        ),
    )
    await command_info.reply(embed=embed)


async def removeWelcomeChannel(command_info: utility.CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.welcome.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await get_welcome_channel(command_info.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.welcome.notSet.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.channel.welcome.notSet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_welcome_channel(command_info.guild.id)  # type: ignore[union-attr]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.welcome.deleteSuccess.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.channel.welcome.deleteSuccess.description",
        ),
    )
    await command_info.reply(embed=embed)


def _process_welcome_image_sync(
    background_frames: list[Image.Image],
    avatar_frames: list[Image.Image],
    user: discord.Member,
    duration: int,
) -> io.BytesIO:
    num_frames = max(len(background_frames), len(avatar_frames))
    background_frames *= (num_frames // len(background_frames)) + 1
    avatar_frames *= (num_frames // len(avatar_frames)) + 1
    background_frames = background_frames[:num_frames]
    avatar_frames = avatar_frames[:num_frames]
    member_number_locale = tanjunLocalizer.localize(
        (user.guild.preferred_locale if hasattr(user.guild, "preferred_locale") else "en"),
        "commands.admin.channel.welcome.memberNumber",
        member_count=user.guild.member_count,
    )

    for i in range(len(background_frames)):
        background_frames[i] = background_frames[i].resize((600, 400))

    for i in range(len(avatar_frames)):
        avatar_frames[i] = avatar_frames[i].resize((150, 150))

    mask = create_circular_mask((150, 150))

    # Create overlay and fonts once before the loop
    overlay = create_overlay((600, 400), (0, 0, 0, 100))
    username_font = load_font("assets/fonts/Arial.ttf", 36)
    info_font = load_font("assets/fonts/Arial.ttf", 24)

    result_frames: list[Image.Image] = []

    for frame_index in range(num_frames):
        bg_frame = background_frames[frame_index]
        avatar_frame = avatar_frames[frame_index]

        frame = bg_frame.copy()

        frame = Image.alpha_composite(frame, overlay)

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

    return save_optimized_gif(result_frames, duration)


async def welcomeNewUser(member: discord.Member) -> None:
    welcome_channel = await get_welcome_channel(member.guild.id)
    if welcome_channel is None:
        return

    if welcome_channel.image_background:
        background_frames, _ = await get_image_or_gif_frames(welcome_channel.image_background)
    else:
        background_frames = []

    avatar_url = str(member.display_avatar.url)
    avatar_frames, avatar_duration = await get_image_or_gif_frames(avatar_url)

    if not background_frames or not avatar_frames:
        return

    # Use avatar duration for the final GIF timing
    duration = avatar_duration if avatar_duration > 0 else 100

    img_byte_arr = await run_in_executor(
        _process_welcome_image_sync,
        background_frames,
        avatar_frames,
        member,
        duration,
    )

    file = discord.File(img_byte_arr, filename="bg.gif")

    description = welcome_channel.message

    if not description:
        description = tanjunLocalizer.localize(
            (member.guild.preferred_locale if hasattr(member.guild, "preferred_locale") else "en"),
            "commands.admin.channel.welcome.success.description",
        )

    description = description.replace("{user}", member.mention)
    description = description.replace("{guild}", member.guild.name)
    description = description.replace("{member}", str(member.guild.member_count))

    embed = utility.tanjunEmbed(
        description=description,
    )
    embed.set_image(url="attachment://bg.gif")

    channel = await member.guild.fetch_channel(int(welcome_channel.channel_id))

    await channel.send(embed=embed, file=file)  # type: ignore[union-attr]
