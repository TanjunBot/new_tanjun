from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import check_if_opted_out, opt_in


async def optIn(commandInfo: commandInfo):
    if not await check_if_opted_out(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.messagetrackingoptin.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.messagetrackingoptin.error.already_opted_in",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await opt_in(commandInfo.user.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.messagetrackingoptin.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.messagetrackingoptin.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
