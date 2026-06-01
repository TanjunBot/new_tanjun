from locale_keys import locale
import io
from typing import Any
import discord
from PIL import Image, ImageDraw
from api import get_user_level_info, set_custom_background
from models import UserLevelInfoModel
from services.pillow_service import create_circular_mask, create_overlay, draw_rounded_rectangle, get_image_or_gif_frames, load_font, run_in_executor, save_optimized_gif
from utility import CommandInfo, draw_text_with_outline, tanjunEmbed, upload_image_to_imgbb

async def show_rankcard_command(command_info: CommandInfo, user: discord.Member) -> None:
    assert command_info.guild is not None
    user_info = await get_user_level_info(str(command_info.guild.id), str(user.id))
    if not user_info:
        embed = tanjunEmbed(title=locale.commands.level.rank.error.no_data.title(str(command_info.locale)), description=locale.commands.level.rank.error.no_data.description(command_info.locale, user=user.mention))
        await command_info.reply(embed=embed)
        return
    rankcard_image = await generate_rankcard(user, user_info, command_info)
    file = discord.File(rankcard_image, filename='rankcard.gif')
    embed = tanjunEmbed(title=locale.commands.level.rank.success.title(str(command_info.locale), user=user.name))
    embed.set_image(url='attachment://rankcard.gif')
    await command_info.reply(embed=embed, file=file)

async def set_background_command(command_info: CommandInfo, image: discord.Attachment) -> None:
    if image.content_type not in ['image/png', 'image/jpeg', 'image/gif']:
        embed = tanjunEmbed(title=locale.commands.level.setbackground.error.invalid_format.title(command_info.locale), description=locale.commands.level.setbackground.error.invalid_format.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    uploaded_image = await upload_image_to_imgbb(await image.read(), image.content_type.split('/')[1])
    await set_custom_background(str(command_info.guild.id), str(command_info.user.id), uploaded_image['data']['url'])
    embed = tanjunEmbed(title=locale.commands.level.setbackground.success.title(str(command_info.locale)), description=locale.commands.level.setbackground.success.description(str(command_info.locale)))
    embed.set_image(url=uploaded_image['data']['url'])
    await command_info.reply(embed=embed)

async def generate_rankcard(user: discord.Member, user_info: dict[str, Any], command_info: CommandInfo) -> io.BytesIO:
    custom_bg = user_info.custom_background
    if custom_bg:
        background_frames, _ = await get_image_or_gif_frames(str(custom_bg))
        if not background_frames:
            background_frames = [Image.open('assets/rankCard.png').convert('RGBA')]
    else:
        background_frames = [Image.open('assets/rankCard.png').convert('RGBA')]
    avatar_url = str(user.display_avatar.url)
    avatar_frames, avatar_duration = await get_image_or_gif_frames(avatar_url)
    if not avatar_frames:
        embed = tanjunEmbed(title=locale.commands.level.rank.error.no_data.title(str(command_info.locale)), description='Failed to load avatar image.')
        await command_info.reply(embed=embed)
        return io.BytesIO()
    avatar_decoration_frames: list[Image.Image] | None = None
    avatar_decoration_url = str(user.avatar_decoration.url) if user.avatar_decoration else None
    if avatar_decoration_url:
        avatar_decoration_frames, _ = await get_image_or_gif_frames(avatar_decoration_url)
        if not avatar_decoration_frames:
            avatar_decoration_frames = None
    duration = avatar_duration if avatar_duration > 0 else 100
    img_byte_arr = await run_in_executor(_process_image_sync, background_frames, avatar_frames, avatar_decoration_frames, user, user_info, command_info, duration)
    if not isinstance(img_byte_arr, io.BytesIO):
        raise TypeError('Expected io.BytesIO from _process_image_sync')
    return img_byte_arr

def _process_image_sync(background_frames: list[Image.Image], avatar_frames: list[Image.Image], avatar_decoration_frames: list[Image.Image] | None, user: discord.Member, user_info: UserLevelInfoModel, command_info: CommandInfo, duration: int) -> io.BytesIO:
    decoration_size_multiplier = 1.2
    num_frames = max(len(background_frames), len(avatar_frames), len(avatar_decoration_frames) if avatar_decoration_frames else 0)
    background_frames *= num_frames // len(background_frames) + 1
    avatar_frames *= num_frames // len(avatar_frames) + 1
    if avatar_decoration_frames:
        avatar_decoration_frames *= num_frames // len(avatar_decoration_frames) + 1
    background_frames = background_frames[:num_frames]
    avatar_frames = avatar_frames[:num_frames]
    if avatar_decoration_frames:
        avatar_decoration_frames = avatar_decoration_frames[:num_frames]
    for i in range(len(background_frames)):
        background_frames[i] = background_frames[i].resize((1000, 300))
    for i in range(len(avatar_frames)):
        avatar_frames[i] = avatar_frames[i].resize((200, 200))
    if avatar_decoration_frames:
        decoration_size = int(200 * decoration_size_multiplier)
        offset = int((decoration_size - 200) / 2)
        for i in range(len(avatar_decoration_frames)):
            avatar_decoration_frames[i] = avatar_decoration_frames[i].resize((decoration_size, decoration_size))
    mask = create_circular_mask((200, 200))
    overlay = create_overlay((1000, 300), (0, 0, 0, 100))
    username_font = load_font('assets/fonts/Arial.ttf', 40)
    info_font = load_font('assets/fonts/Arial.ttf', 30)
    result_frames: list[Image.Image] = []
    for frame_index in range(num_frames):
        bg_frame = background_frames[frame_index]
        frame = bg_frame.copy()
        frame = Image.alpha_composite(frame, overlay)
        draw = ImageDraw.Draw(frame)
        draw_text_with_outline(draw, (250, 50), user.name, username_font, (255, 255, 255, 255), (0, 0, 0, 255))
        draw_text_with_outline(draw, (250, 105), locale.commands.level.rank.data.level(str(command_info.locale), level=user_info.level), info_font, (255, 255, 255, 255), (0, 0, 0, 255))
        draw_text_with_outline(draw, (250, 150), locale.commands.level.rank.data.xp(command_info.locale, xp=user_info.xp, xp_needed=user_info.xp_needed), info_font, (255, 255, 255, 255), (0, 0, 0, 255))
        bar_width = 700
        bar_height = 30
        xp_percentage = user_info.xp / (user_info.xp_needed if user_info.xp_needed > 0 else 1)
        filled_width = int(bar_width * xp_percentage)
        radius = bar_height // 4
        draw_rounded_rectangle(draw, [250, 200, 250 + bar_width, 200 + bar_height], radius, fill=(50, 50, 50, 200), outline=(255, 255, 255, 255), width=2)
        if xp_percentage >= 0.02:
            draw_rounded_rectangle(draw, [250, 200, 250 + filled_width, 200 + bar_height], radius, fill=(127, 219, 255, 200), outline=(255, 255, 255, 200), width=2)
        output = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        output.paste(avatar_frames[frame_index], (0, 0), mask)
        frame.paste(output, (25, 50), output)
        if avatar_decoration_frames:
            decoration = avatar_decoration_frames[frame_index]
            decoration = decoration.resize((decoration_size, decoration_size)).convert('RGBA')
            decoration_layer = Image.new('RGBA', frame.size, (0, 0, 0, 0))
            decoration_layer.paste(decoration, (25 - offset, 50 - offset), decoration)
            frame = Image.alpha_composite(frame, decoration_layer)
        result_frames.append(frame)
    return save_optimized_gif(result_frames, duration)