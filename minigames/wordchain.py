import asyncio
import logging

import discord

from api import check_if_opted_out, clear_wordchain, get_wordchain_last_user_id, get_wordchain_word, set_wordchain_word
from localizer import tanjunLocalizer
from utility import tanjunEmbed

logger = logging.getLogger(__name__)


async def wordchain(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.guild == None:
        embed: discord.Embed = tanjunEmbed(
            title=tanjunLocalizer.localize("en_US", "errors.guildonly.title"),
            description=tanjunLocalizer.localize(
                "en_US",
                "errors.guildonly.description",
            ),
        )
        await message.channel.send(embed=embed)
        return

    wordchain_word = await get_wordchain_word(message.channel.id)
    if wordchain_word is None:
        return

    locale = str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"

    if await check_if_opted_out(message.author.id):
        results = await asyncio.gather(
            message.author.send(tanjunLocalizer.localize(locale, "minigames.wordchain.opted_out")),
            message.delete(),
            return_exceptions=True,
        )
        for r in results:
            if isinstance(r, Exception):
                logger.warning("Error in wordchain opted_out handler: %s", r)
        return

    content = message.content

    if not content:
        await message.delete()
        return

    if content.count(" ") > 0:
        await message.delete()
        return

    if str(await get_wordchain_last_user_id(message.channel.id)) == str(message.author.id):
        await message.delete()
        return

    endChars = (".", "?", "!", ";", ":")

    for char in content:
        if char in endChars:
            new_sentence = wordchain_word + content
            embed = tanjunEmbed(
                title=tanjunLocalizer.localize(locale, "minigames.wordchain.finished.title"),
                description=tanjunLocalizer.localize(
                    locale,
                    "minigames.wordchain.finished.description",
                    sentence=new_sentence,
                ),
            )
            results = await asyncio.gather(
                clear_wordchain(message.channel.id),
                set_wordchain_word(channel_id=message.channel.id, guild_id=message.guild.id, word="", worder_id="nobody"),
                message.channel.send(embed=embed),
                return_exceptions=True,
            )
            for r in results:
                if isinstance(r, Exception):
                    logger.warning("Error in wordchain finished handler: %s", r)
            return

    if content == ",":
        await set_wordchain_word(
            channel_id=message.channel.id, guild_id=message.guild.id, word=wordchain_word + ",", worder_id="nobody"
        )
        return

    await set_wordchain_word(
        channel_id=message.channel.id,
        guild_id=message.guild.id,
        word=wordchain_word + " " + content,
        worder_id=message.author.id,
    )
