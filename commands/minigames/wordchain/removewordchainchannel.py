from api import get_wordchain_word, clear_wordchain
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
import discord


async def removewordchainchannel(
    commandInfo: commandInfo, channel: discord.TextChannel
):

    if not commandInfo.user.guild_permissions.moderate_members:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removewordchainchannel.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removewordchainchannel.error.no_moderate_members_perms.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check if the channel is a counting channel
    current_progress = await get_wordchain_word(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removewordchainchannel.error.not_counting_channel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "minigames.removewordchainchannel.error.not_counting_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await clear_wordchain(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "minigames.removewordchainchannel.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removewordchainchannel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)

    # Send a message to the channel informing users it's no longer a counting channel
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "minigames.removewordchainchannel.channel_message.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "minigames.removewordchainchannel.channel_message.description",
        ),
    )
    await channel.send(embed=info_embed)
