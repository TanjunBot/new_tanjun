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


async def setCountingProgress(command_info: CommandInfo, channel: discord.TextChannel, progress: int) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(command_info, channel.id, get_counting_progress, LOCALE_KEY)
    if current_progress is None:
        return

    if await require_valid_progress(command_info, progress, LOCALE_KEY):
        return

    await set_counting_progress(channel.id, progress, command_info.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.success.description").format(
            channel=channel.mention, progress=progress
        ),
    )
    await command_info.reply(embed=embed)

    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.channel_message.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.channel_message.description").format(
            progress=progress
        ),
    )
    await channel.send(embed=info_embed)
