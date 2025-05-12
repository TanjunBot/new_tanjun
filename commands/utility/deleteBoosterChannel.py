import discord

import utility
from api import delete_booster_channel, get_booster_channel
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def deleteBoosterChannel(commandInfo: commandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterchannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterchannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    booster_channel = await get_booster_channel(commandInfo.guild.id)
    if not booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterchannel.no_booster_channel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.deleteboosterchannel.no_booster_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await delete_booster_channel(commandInfo.guild.id, booster_channel)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.deleteboosterchannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.deleteboosterchannel.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
