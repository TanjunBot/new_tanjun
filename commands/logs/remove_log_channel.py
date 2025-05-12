import utility
from api import (
    get_log_channel as get_log_channel_api,
)
from api import (
    remove_log_channel as remove_log_channel_api,
)
from localizer import tanjunLocalizer


async def remove_log_channel(commandInfo: utility.commandInfo):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.removeLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.removeLogChannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    logChannel = await get_log_channel_api(commandInfo.guild.id)

    if not logChannel:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.removeLogChannel.notSet.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.removeLogChannel.notSet.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_log_channel_api(commandInfo.guild.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.removeLogChannel.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.removeLogChannel.success.description"),
    )
    await commandInfo.reply(embed=embed)
