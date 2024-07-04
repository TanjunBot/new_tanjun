from api import get_counting_progress, get_last_counter_id, check_if_opted_out, increase_counting_progress
import discord
from localizer import tanjunLocalizer
import random

async def counting(message: discord.Message):
    if message.author.bot:
        return

    progress = await get_counting_progress(message.channel.id)

    locale = message.guild.locale if hasattr(message.guild, "locale") else "en_US"

    if not progress and progress != 0:
        return
    
    if await check_if_opted_out(message.author.id):
        try:
            await message.author.send(tanjunLocalizer.localize(locale, "minigames.counting.opted_out"))
        except discord.Forbidden:
            pass
        await message.delete()
        return

    content = message.content

    if not content:
        await message.delete()
        return

    if not content.isdigit():
        await message.delete()
        return

    number = int(content)

    if number != progress + 1:
        await message.delete()
        return

    last_counter_id = await get_last_counter_id(message.channel.id)

    if last_counter_id == str(message.author.id):
        await message.delete()
        return

    await increase_counting_progress(message.channel.id, message.author.id)
    #nosec: B311
    if random.randint(1, 100) == 1:
        await message.channel.send(progress + 2)
        await increase_counting_progress(message.channel.id, "me")