import discord

from api import get_counting_progress, set_counting_progress
from commands.minigames._counting_common import (
    require_counting_channel,
    require_moderate_members,
    require_valid_progress,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.setcountingprogress"


async def setCountingProgress(commandInfo: CommandInfo, channel: discord.TextChannel, progress: int) -> None:
    if await require_moderate_members(commandInfo, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(commandInfo, channel.id, get_counting_progress, LOCALE_KEY)
    if current_progress is None:
        return

    if await require_valid_progress(commandInfo, progress, LOCALE_KEY):
        return

    await set_counting_progress(channel.id, progress, commandInfo.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.success.description").format(
            channel=channel.mention, progress=progress
        ),
    )
    await commandInfo.reply(embed=embed)

    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.channel_message.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, f"{LOCALE_KEY}.channel_message.description").format(progress=progress),
    )
    await channel.send(embed=info_embed)
