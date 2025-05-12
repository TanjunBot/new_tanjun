from api import get_levelup_message_status, set_levelup_message_status
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def disable_levelup_message(commandInfo: commandInfo):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelupmessage.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_status = await get_levelup_message_status(str(commandInfo.guild.id))
    if not current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelupmessage.error.already_disabled.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.disablelevelupmessage.error.already_disabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_levelup_message_status(str(commandInfo.guild.id), False)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.disablelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.disablelevelupmessage.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
