import discord

from api import set_counting_progress
from commands.minigames._counting_common import (
    require_bot_permissions,
    require_moderate_members,
)
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed

LOCALE_KEY = "minigames.setcountingchannel"


async def setCountingChannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if await require_moderate_members(command_info, LOCALE_KEY):
        return

    if command_info.guild is None:
        return

    if await require_bot_permissions(command_info, channel):
        return

    await set_counting_progress(channel_id=channel.id, guild_id=command_info.guild.id, progress=0)

    introduction_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.introduction.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.introduction.description"),
    )
    await channel.send(embed=introduction_embed)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), f"{LOCALE_KEY}.success.title"),
        description=tanjunLocalizer.localize(command_info.locale, f"{LOCALE_KEY}.success.description", channel=channel.mention),
    )
    await command_info.reply(embed=embed)
