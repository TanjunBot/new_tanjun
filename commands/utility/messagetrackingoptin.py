from api import check_if_opted_out, opt_in
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def optIn(command_info: CommandInfo) -> None:
    if not await check_if_opted_out(command_info.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.messagetrackingoptin.error.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.messagetrackingoptin.error.already_opted_in",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await opt_in(command_info.user.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.messagetrackingoptin.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.messagetrackingoptin.success.description",
        ),
    )
    await command_info.reply(embed=embed)
