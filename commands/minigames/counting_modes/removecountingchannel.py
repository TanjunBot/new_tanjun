import discord

from commands.minigames._counting_common import require_counting_channel, require_moderate_members
from localizer import tanjunLocalizer
from services.counting_repository import CountingMode, CountingRepository
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.removecountingmodeschannel"
_repo = CountingRepository


async def removecountingmodeschannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(
        command_info, channel.id,
        lambda cid: _repo.get_progress(CountingMode.MODES, cid),
        LOCALE_KEY,
    )
    if current_progress is None:
        return

    await _repo.clear(CountingMode.MODES, channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.success.description", channel=channel.mention),
    )
    await command_info.reply(embed=embed)

    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.channel_message.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.channel_message.description"),
    )
    await channel.send(embed=info_embed)
