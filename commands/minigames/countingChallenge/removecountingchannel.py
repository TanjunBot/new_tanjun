import discord

from api import clear_counting_challenge, get_counting_challenge_progress
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def removecountingchallengechannel(commandInfo: commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).moderate_members
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchallengechannel.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchallengechannel.error.no_moderate_members_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check if the channel is a counting channel
    current_progress = await get_counting_challenge_progress(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchallengechannel.error.not_counting_channel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchallengechannel.error.not_counting_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Remove the channel from the counting database
    await clear_counting_challenge(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.removecountingchallengechannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removecountingchallengechannel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users it's no longer a counting channel
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removecountingchallengechannel.channel_message.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removecountingchallengechannel.channel_message.description",
        ),
    )
    await channel.send(embed=info_embed)
