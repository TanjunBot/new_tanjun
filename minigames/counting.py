import random

import discord

from api import check_if_opted_out, get_counting_progress, get_last_counter_id, increase_counting_progress
from localizer import tanjunLocalizer
from utility import tanjunEmbed


async def counting(message: discord.Message) -> None:
    if message.author.bot:
        return

    if (message.guild == None):
        embed: discord.Embed = tanjunEmbed(
                title=tanjunLocalizer.localize("en_US", "errors.guildonly.title"),
                description=tanjunLocalizer.localize(
                    "en_US",
                    "errors.guildonly.description",
                ),
            )
        await message.channel.send(embed=embed)
        return

    progress = await get_counting_progress(message.channel.id)

    locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"

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
    # nosec: B311
    if random.randint(1, 100) == 1:
        await message.channel.send(str(progress + 2))
        await increase_counting_progress(message.channel.id, "me")
