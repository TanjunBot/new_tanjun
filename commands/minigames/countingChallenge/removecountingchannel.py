from api import get_counting_challenge_progress, clear_counting_challenge
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
import discord

async def removecountingmodeschannel(commandInfo: commandInfo, channel: discord.TextChannel):

    if not commandInfo.user.guild_permissions.moderate_members:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.error.no_moderate_members_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.error.no_moderate_members_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    # Check if the channel is a counting channel
    current_progress = get_counting_challenge_progress(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.error.not_counting_channel.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.error.not_counting_channel.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    # Remove the channel from the counting database
    clear_counting_challenge(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.success.description", channel=channel.mention),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users it's no longer a counting channel
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.channel_message.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.removecountingmodeschannel.channel_message.description"),
    )
    await channel.send(embed=info_embed)