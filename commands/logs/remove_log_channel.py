import discord

import utility
from api import (
    get_log_channel as get_log_channel_api,
)
from api import (
    remove_log_channel as remove_log_channel_api,
)
from localizer import tanjunLocalizer


async def remove_log_channel(command_info: utility.CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.removeLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.removeLogChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    log_channel = await get_log_channel_api(command_info.guild.id)

    if not log_channel:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.removeLogChannel.notSet.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.logs.removeLogChannel.notSet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_log_channel_api(command_info.guild.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.removeLogChannel.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.removeLogChannel.success.description"),
    )
    await command_info.reply(embed=embed)
