import utility
from localizer import tanjunLocalizer
from services.ai_service import AiService


async def delete_custom_situation(
    command_info: utility.CommandInfo,
) -> None:
    situation = await AiService.get_user_situation(command_info.user.id)

    if situation is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.notfound.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.notfound.description"),
        )
        await command_info.reply(embed=embed)
        return

    await AiService.delete_situation(situation.user_id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.ai.deletecustom.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.ai.deletecustom.success.description",
            name=situation.name,
        ),
    )
    await command_info.reply(embed=embed)
