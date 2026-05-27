from api import check_if_opted_out, opt_out
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def optOut(command_info: CommandInfo) -> None:
    if await check_if_opted_out(command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.messagetrackingoptout.error.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.messagetrackingoptout.error.already_opted_out",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await opt_out(command_info.user.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.messagetrackingoptout.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.messagetrackingoptout.success.description",
        ),
    )
    await command_info.reply(embed=embed)
