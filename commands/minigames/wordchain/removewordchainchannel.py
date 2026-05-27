import discord

from api import clear_wordchain, get_wordchain_word
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def removewordchainchannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        return
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).moderate_members
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.removewordchainchannel.error.no_moderate_members_perms.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.removewordchainchannel.error.no_moderate_members_perms.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    # Check if the channel is a counting channel
    current_progress = await get_wordchain_word(channel.id)
    if current_progress is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.removewordchainchannel.error.not_counting_channel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "minigames.removewordchainchannel.error.not_counting_channel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await clear_wordchain(channel.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "minigames.removewordchainchannel.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "minigames.removewordchainchannel.success.description",
            channel=channel.mention,
        ),
    )
    await command_info.reply(embed=embed)

    # Send a message to the channel informing users it's no longer a counting channel
    info_embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "minigames.removewordchainchannel.channel_message.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "minigames.removewordchainchannel.channel_message.description",
        ),
    )
    await channel.send(embed=info_embed)
