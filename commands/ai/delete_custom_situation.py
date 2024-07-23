import utility
from localizer import tanjunLocalizer
from api import getCustomSituationFromUser, deleteCustomSituation

async def delete_custom_situation(
        commandInfo: utility.commandInfo,
):
    situation = await getCustomSituationFromUser(commandInfo.user.id)

    if situation is None:
        embed = utility.tanjunEmbed(
            title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.deletecustom.notfound.title"),
            description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.deletecustom.notfound.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    await deleteCustomSituation(situation[0])
    
    embed = utility.tanjunEmbed(
        title = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.deletecustom.success.title"),
        description = tanjunLocalizer.localize(commandInfo.locale, "commands.ai.deletecustom.success.description", name=situation[2]),
    )
    await commandInfo.reply(embed=embed)