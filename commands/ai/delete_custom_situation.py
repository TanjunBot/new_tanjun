import utility
from api import deleteCustomSituation, getCustomSituationFromUser
from localizer import tanjunLocalizer


async def delete_custom_situation(
    command_info: utility.CommandInfo,
) -> None:
    situation = await getCustomSituationFromUser(command_info.user.id)

    if situation is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.notfound.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.notfound.description"),
        )
        await command_info.reply(embed=embed)
        return

    await deleteCustomSituation(situation.user_id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.ai.deletecustom.success.description",
            name=situation.name,
        ),
    )
    await command_info.reply(embed=embed)
