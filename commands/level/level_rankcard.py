import discord
from utility import commandInfo, tanjunEmbed, checkIfhasPlus
from localizer import tanjunLocalizer
from api import get_user_level_info, set_custom_background
from imgurpython import ImgurClient
import config
from PIL import Image, ImageDraw, ImageFont
import io
import requests
from typing import Tuple
import tempfile
import asyncio
import os
from io import BytesIO
import aiohttp

async def upload_image_to_imgbb(image_bytes, file_extension):
    # Create a temporary file with the appropriate file extension
    with tempfile.NamedTemporaryFile(delete=False, suffix="." + file_extension, mode='wb') as temp_file:
        temp_file.write(image_bytes)
        temp_file_path = temp_file.name

    # Upload the image to ImgBB
    async with aiohttp.ClientSession() as session:
        with open(temp_file_path, 'rb') as image_file:
            form_data = aiohttp.FormData()
            form_data.add_field('key', config.ImgBBApiKey)
            form_data.add_field('image', image_file)
            form_data.add_field('name', f'tbg')

            async with session.post('https://api.imgbb.com/1/upload', data=form_data) as response:
                response_data = await response.json()

    # Optionally, delete the temporary file if you want to clean up
    os.remove(temp_file_path)

    return response_data


async def show_rankcard_command(commandInfo: commandInfo, user: discord.Member):
    user_info = get_user_level_info(str(commandInfo.guild.id), str(user.id))
    
    if not user_info:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.rank.error.no_data.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.rank.error.no_data.description",
                user=user.mention
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    rankcard_image = await generate_rankcard(user, user_info)
    
    file = discord.File(rankcard_image, filename="rankcard.png")
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.rank.success.title",
            user=user.name
        ),
    )
    embed.set_image(url="attachment://rankcard.png")
    
    await commandInfo.reply(embed=embed, file=file)

async def set_background_command(commandInfo: commandInfo, image: discord.Attachment):
    if not checkIfhasPlus(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setbackground.error.no_plus.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setbackground.error.no_plus.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if image.content_type not in ['image/png', 'image/jpeg', 'image/gif']:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setbackground.error.invalid_format.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setbackground.error.invalid_format.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    uploaded_image = await upload_image_to_imgbb(await image.read(), image.content_type.split("/")[1])

    print(uploaded_image)

    set_custom_background(str(commandInfo.guild.id), str(commandInfo.user.id), uploaded_image["data"]["url"])

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

async def generate_rankcard(user: discord.Member, user_info: dict) -> io.BytesIO:
    # Load background image
    if user_info['customBackground']:
        response = requests.get(user_info['customBackground'])
        image_data = BytesIO(response.content)
        background = Image.open(image_data).convert("RGBA")

    else:
        background = Image.open("assets/rankCard.png").convert("RGBA")

    # Resize background to 1000x300 if needed
    background = background.resize((1000, 300))

    # Create a drawing object
    draw = ImageDraw.Draw(background)

    # Load fonts
    username_font = ImageFont.truetype("assets/fonts/Arial.ttf", 40)
    info_font = ImageFont.truetype("assets/fonts/Arial.ttf", 30)

    # Draw username
    draw.text((250, 50), user.name, font=username_font, fill=(255, 255, 255, 128))

    # Draw level and XP
    draw.text((250, 100), f"Level: {user_info['level']}", font=info_font, fill=(255, 255, 255, 128))
    draw.text((250, 150), f"XP: {user_info['xp']}/{user_info['xp_needed']}", font=info_font, fill=(255, 255, 255, 128))

    # Draw XP bar
    bar_width = 700
    bar_height = 30
    xp_percentage = user_info['xp'] / user_info['xp_needed']
    filled_width = int(bar_width * xp_percentage)

    draw.rectangle([250, 200, 250 + bar_width, 200 + bar_height], fill=(100, 100, 100, 128))
    draw.rectangle([250, 200, 250 + filled_width, 200 + bar_height], fill=(0, 255, 0, 128))

    # Add user avatar
    avatar_url = str(user.display_avatar.url)
    avatar_response = requests.get(avatar_url)
    avatar_image = Image.open(io.BytesIO(avatar_response.content))
    avatar_image = avatar_image.resize((200, 200))

    # Create circular mask for avatar
    mask = Image.new('L', (200, 200), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 200, 200), fill=255)

    # Apply circular mask to avatar
    output = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
    output.paste(avatar_image, (0, 0), mask)

    # Paste avatar onto background
    background.paste(output, (25, 50), output)

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    background.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr