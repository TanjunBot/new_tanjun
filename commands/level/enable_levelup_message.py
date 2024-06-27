from utility import commandInfo, tanjunEmbed, checkIfHasPro
from localizer import tanjunLocalizer
from api import set_levelup_message_status, get_levelup_message_status

async def enable_levelup_message(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.no_permission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.no_pro.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.no_pro.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_status = get_levelup_message_status(str(commandInfo.guild.id))
    if current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.already_enabled.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelupmessage.error.already_enabled.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    set_levelup_message_status(str(commandInfo.guild.id), True)
    
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.enablelevelupmessage.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.enablelevelupmessage.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)