import contextlib

import utility
from localizer import tanjunLocalizer
from services.ai_service import AiService


async def approve_custom_situation(interaction) -> None:  # type: ignore[no-untyped-def]
    situation_id = interaction.data["custom_id"].split(";")[1]
    situation = await AiService.get_user_situation(situation_id)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return
    situation_creator = interaction.client.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(
            "Der typ der die Situation erstellt hat ist nicht mehr am tanjun nutzen :c",
            delete_after=25,
        )
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.title"),
        description=tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.description"),
    )

    await AiService.unlock_situation(situation_id)
    try:
        await situation_creator.send(embed=embed)
    # flake8: noqa: E722
    except:
        pass
    await interaction.channel.send("Situation wurde freigeschaltet!", delete_after=25)


async def deny_custom_situation(interaction) -> None:  # type: ignore[no-untyped-def]
    situation_id = interaction.data["custom_id"].split(";")[1]
    situation = await AiService.get_user_situation(situation_id)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return

    situation_creator = interaction.bot.get_user(int(situation_id))
    if not situation_creator:
        await interaction.channel.send(
            "Der typ der die Situation erstellt hat ist nicht mehr am tanjun nutzen :c",
            delete_after=25,
        )
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.title"),
        description=tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.description"),
    )

    await AiService.delete_situation(situation_id)
    with contextlib.suppress(BaseException):
        await situation_creator.send(embed=embed)
    await interaction.channel.send("Situation wurde gelöscht!", delete_after=25)
