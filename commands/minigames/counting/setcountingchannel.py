import discord

from api import set_counting_progress
from commands.minigames._counting_common import (
    require_bot_permissions,
    require_moderate_members,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.setcountingchannel"


async def setCountingChannel(commandInfo: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(commandInfo, LOCALE_KEY):
        return

    if commandInfo.guild is None:
        return

    if await require_bot_permissions(commandInfo, channel):
        return

    await set_counting_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)

    introduction_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.introduction.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.introduction.description"),
    )
    await channel.send(embed=introduction_embed)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, f"{LOCALE_KEY}.success.description", channel=channel.mention),
    )
    await commandInfo.reply(embed=embed)
