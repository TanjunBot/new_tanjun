from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import set_level_system_status, get_level_system_status

async def enable_level_system(commandInfo: commandInfo):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelsystem.error.no_permission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelsystem.error.no_permission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_status = get_level_system_status(str(commandInfo.guild.id))
    
    if current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelsystem.error.already_enabled.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.enablelevelsystem.error.already_enabled.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    set_level_system_status(str(commandInfo.guild.id), True)
    
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.enablelevelsystem.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.enablelevelsystem.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)