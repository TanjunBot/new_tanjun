import utility
from localizer import tanjunLocalizer
from api import unlockCustomSituation, getCustomSituationFromUser, deleteCustomSituation
import discord

async def approve_custom_situation(interaction):
    situationId = interaction.data["custom_id"].split(";")[1]
    situation = await getCustomSituationFromUser(situationId)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return
    situationCreator = interaction.client.get_user(int(situationId))
    if not situationCreator:
        await interaction.response.send_message("Der typ der die Situation erstellt hat ist nicht mehr am tanjun nutzen :c")
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.title"),
        description = tanjunLocalizer.localize(locale, "commands.ai.approvecustom.success.description"),
    )

    await unlockCustomSituation(situationId)
    try:
        await situationCreator.send(embed=embed)
    except:
        pass
    await interaction.response.send_message("Situation wurde freigeschaltet!")

async def deny_custom_situation(interaction):
    situationId = interaction.data["custom_id"].split(";")[1]
    situation = await getCustomSituationFromUser(situationId)
    if not situation:
        await interaction.response.send_message("Situation wurde denke gelöscht oder so :/")
        return
    
    situationCreator = interaction.bot.get_user(int(situationId))
    if not situationCreator:
        await interaction.response.send_message("Der typ der die Situation erstellt hat ist nicht mehr am tanjun nutzen :c")
        return

    locale = interaction.data["custom_id"].split(";")[2]

    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.title"),
        description = tanjunLocalizer.localize(locale, "commands.ai.dencustom.success.description"),
    )

    await deleteCustomSituation(situationId)
    try:
        await situationCreator.send(embed=embed)
    except:
        pass
    await interaction.response.send_message("Situation wurde gelöscht!")