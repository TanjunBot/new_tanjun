from api import get_levelup_message_status, set_levelup_message_status
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def enable_levelup_message(commandInfo: commandInfo):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.enablelevelupmessage.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.enablelevelupmessage.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    current_status = await get_levelup_message_status(str(commandInfo.guild.id))
    if current_status:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.enablelevelupmessage.error.already_enabled.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.enablelevelupmessage.error.already_enabled.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_levelup_message_status(str(commandInfo.guild.id), True)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.enablelevelupmessage.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.enablelevelupmessage.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
