from api import get_brawlstars_linked_account, remove_brawlstars_linked_account
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def unlink(commandInfo: commandInfo):
    if not await get_brawlstars_linked_account(commandInfo.user.id):
        return await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.unlink.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.unlink.error.notLinked.description",
                ),
            )
        )

    await remove_brawlstars_linked_account(commandInfo.user.id)

    return await commandInfo.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.unlink.success.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.unlink.success.description",
            ),
        )
    )
