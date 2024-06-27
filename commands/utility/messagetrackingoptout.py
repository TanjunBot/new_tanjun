from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import check_if_opted_out, opt_in, opt_out

async def optOut(commandInfo: commandInfo):
    if check_if_opted_out(commandInfo.user.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.messagetrackingoptout.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.messagetrackingoptout.error.already_opted_out"
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    
    opt_out(commandInfo.user.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.messagetrackingoptout.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.messagetrackingoptout.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)