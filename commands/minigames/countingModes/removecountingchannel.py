import discord

from api import clear_counting_mode, get_counting_mode_progress
from commands.minigames._counting_common import require_counting_channel, require_moderate_members
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.removecountingmodeschannel"


async def removecountingmodeschannel(commandInfo: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(commandInfo, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(commandInfo, channel.id, get_counting_mode_progress, LOCALE_KEY)
    if current_progress is None:
        return

    await clear_counting_mode(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, f"{LOCALE_KEY}.success.description", channel=channel.mention),
    )
    await commandInfo.reply(embed=embed)

    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, f"{LOCALE_KEY}.channel_message.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, f"{LOCALE_KEY}.channel_message.description"),
    )
    await channel.send(embed=info_embed)
