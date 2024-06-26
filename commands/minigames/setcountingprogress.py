from api import set_counting_progress, get_counting_progress
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
import discord

async def setCountingProgress(commandInfo: commandInfo, channel: discord.TextChannel, progress: int):
    # Check if the channel is a counting channel
    current_progress = get_counting_progress(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.error.not_counting_channel.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.error.not_counting_channel.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check if the new progress is valid (non-negative)
    if progress < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.error.invalid_progress.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.error.invalid_progress.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    # Set the new progress
    set_counting_progress(channel.id, progress, commandInfo.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.success.description").format(channel=channel.mention, progress=progress),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users about the new progress
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.channel_message.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingprogress.channel_message.description").format(progress=progress),
    )
    await channel.send(embed=info_embed)