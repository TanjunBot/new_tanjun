"""Set counting challenge progress (matching original behavior under counting_modes directory)."""

import discord

from commands.minigames._counting_common import (
    require_counting_channel,
    require_moderate_members,
    require_valid_progress,
)
from localizer import tanjunLocalizer
from services.counting_repository import CountingMode, CountingRepository
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.setcountingchallengeprogress"
_repo = CountingRepository


async def setCountingProgress(command_info: CommandInfo, channel: discord.TextChannel, progress: int) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(
        command_info,
        channel.id,
        lambda cid: _repo.get_progress(CountingMode.MODES, cid),
        LOCALE_KEY,
    )
    if current_progress is None:
        return

    if await require_valid_progress(command_info, progress, LOCALE_KEY):
        return

    await _repo.set_challenge_progress(CountingMode.MODES, channel.id, progress)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.success.description").format(
            channel=channel.mention, progress=progress
        ),
    )
    await command_info.reply(embed=embed)

    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.channel_message.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.channel_message.description").format(
            progress=progress
        ),
    )
    await channel.send(embed=info_embed)
