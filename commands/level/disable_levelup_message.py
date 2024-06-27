from utility import commandInfo, tanjunEmbed, checkIfHasPro
from localizer import tanjunLocalizer
from api import set_levelup_message_status, get_levelup_message_status

async def disable_levelup_message(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelupmessage.error.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelupmessage.error.no_permission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_status = get_levelup_message_status(str(commandInfo.guild.id))
    if not current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelupmessage.error.already_disabled.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.disablelevelupmessage.error.already_disabled.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    set_levelup_message_status(str(commandInfo.guild.id), False)
    
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.disablelevelupmessage.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.disablelevelupmessage.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)