from api import set_counting_challenge_progress, get_counting_challenge_progress
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
import discord

async def setCountingProgress(commandInfo: commandInfo, channel: discord.TextChannel, progress: int):

    if not commandInfo.user.guild_permissions.moderate_members:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.no_moderate_members_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.no_moderate_members_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    current_progress = await get_counting_challenge_progress(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.not_counting_channel.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.not_counting_channel.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if progress < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.invalid_progress.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.invalid_progress.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if progress > 1_000_000_000:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.too_high.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.error.too_high.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    # Set the new progress
    await set_counting_challenge_progress(channel.id, progress, commandInfo.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.success.description").format(channel=channel.mention, progress=progress),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users about the new progress
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.channel_message.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchallengeprogress.channel_message.description").format(progress=progress),
    )
    await channel.send(embed=info_embed)