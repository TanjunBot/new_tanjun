from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_booster_channel, delete_booster_channel
import utility


async def deleteBoosterChannel(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
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

    await delete_booster_channel(commandInfo.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.deleteboosterchannel.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.deleteboosterchannel.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
