from api import get_brawlstars_linked_account, remove_brawlstars_linked_account
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def unlink(command_info: CommandInfo) -> None:
    if not await get_brawlstars_linked_account(command_info.user.id):
        await command_info.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.unlink.error.notLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.brawlstars.unlink.error.notLinked.description",
                ),
            )
        )
        return

    await remove_brawlstars_linked_account(command_info.user.id)

    await command_info.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.unlink.success.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.brawlstars.unlink.success.description",
            ),
        )
    )
