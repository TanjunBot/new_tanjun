import discord  # type: ignore[import-not-found]

from api import clear_counting, get_counting_progress
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def removeCountingChannel(commandInfo: CommandInfo, channel: discord.TextChannel) -> None:  # type: ignore[no-any-unimported]
    if commandInfo.guild is None:
        return
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).moderate_members
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchannel.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchannel.error.no_moderate_members_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check if the channel is a counting channel
    current_progress = await get_counting_progress(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchannel.error.not_counting_channel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removecountingchannel.error.not_counting_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Remove the channel from the counting database
    await clear_counting(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.removecountingchannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removecountingchannel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users it's no longer a counting channel
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "minigames.removecountingchannel.channel_message.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removecountingchannel.channel_message.description",
        ),
    )
    await channel.send(embed=info_embed)
