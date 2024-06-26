from api import get_counting_progress, get_last_counter_id, check_if_opted_out, increase_counting_progress
import discord
from localizer import tanjunLocalizer
import random

async def counting(message: discord.Message):
    if message.author.bot:
        return

    progress = get_counting_progress(message.channel.id)

    locale = message.guild.locale if hasattr(message.guild, "locale") else "en_US"

    if not progress:
        return
    
    if check_if_opted_out(message.author.id):
        try:
            await message.author.send(tanjunLocalizer.localize(locale, "minigames.counting.opted_out"))
        except discord.Forbidden:
            pass
        await message.delete(reason = tanjunLocalizer.localize(locale, "minigames.counting.reasons.opted_out"))
        return

    content = message.content

    if not content:
        await message.delete(reason = tanjunLocalizer.localize(locale, "minigames.counting.reasons.empty"))
        return

    if not content.isdigit():
        await message.delete(reason = tanjunLocalizer.localize(locale, "minigames.counting.reasons.not_number"))
        return

    number = int(content)

    if number != progress + 1:
        await message.delete(reason = tanjunLocalizer.localize(locale, "minigames.counting.reasons.wrong_number"))
        return

    last_counter_id = get_last_counter_id(message.channel.id)

    if last_counter_id == message.author.id:
        await message.delete(reason = tanjunLocalizer.localize(locale, "minigames.counting.reasons.double_counter"))
        return

    increase_counting_progress(message.channel.id, message.author.id)
    if random.randint(1, 100) == 1:
        await message.channel.send(progress + 2)
        increase_counting_progress(message.channel.id, "me")