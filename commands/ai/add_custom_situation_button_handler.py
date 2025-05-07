import utility
from api import deleteCustomSituation, getCustomSituationFromUser, unlockCustomSituation
from localizer import tanjunLocalizer


async def approve_custom_situation(interaction):
    situationId = interaction.data["custom_id"].split(";")[1]
    situation = await getCustomSituationFromUser(situationId)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return
    situationCreator = interaction.client.get_user(int(situationId))
    if not situationCreator:
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

    await unlockCustomSituation(situationId)
    try:
        await situationCreator.send(embed=embed)
    # flake8: noqa: E722
    except:
        pass
    await interaction.channel.send("Situation wurde freigeschaltet!", delete_after=25)


async def deny_custom_situation(interaction):
    situationId = interaction.data["custom_id"].split(";")[1]
    situation = await getCustomSituationFromUser(situationId)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return

    situationCreator = interaction.bot.get_user(int(situationId))
    if not situationCreator:
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

    await deleteCustomSituation(situationId)
    try:
        await situationCreator.send(embed=embed)
    except:
        pass
    await interaction.channel.send("Situation wurde gelöscht!", delete_after=25)
