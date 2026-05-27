import discord

from api import clear_counting_challenge, get_counting_challenge_progress
from commands.minigames._counting_common import require_counting_channel, require_moderate_members
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.removecountingchallengechannel"


async def removecountingchallengechannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return

    current_progress = await require_counting_channel(command_info, channel.id, get_counting_challenge_progress, LOCALE_KEY)
    if current_progress is None:
        return

    await clear_counting_challenge(channel.id)

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
