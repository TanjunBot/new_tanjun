from api import set_levelup_message
from localizer import tanjunLocalizer
from utility import checkIfHasPro, commandInfo, tanjunEmbed


async def change_levelup_message(commandInfo: commandInfo, new_message: str):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.no_pro.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.no_pro.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if len(new_message) > 255:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.message_too_long.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.changelevelupmessage.error.message_too_long.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_levelup_message(str(commandInfo.guild.id), new_message)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.level.changelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.changelevelupmessage.success.description",
            new_message=new_message,
        ),
    )
    await commandInfo.reply(embed=embed)
