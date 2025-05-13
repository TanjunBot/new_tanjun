import discord

import utility
from api import (
    get_log_channel as get_log_channel_api,
)
from api import (
    set_log_channel as set_log_channel_api,
)
from localizer import tanjunLocalizer


async def set_log_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    selfMember = commandInfo.guild.get_member(commandInfo.client.user.id)
    permissions = channel.permissions_for(selfMember)

    if not permissions.send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.botMissingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.setLogChannel.botMissingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    logChannel = await get_log_channel_api(commandInfo.guild.id)

    if logChannel:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.setLogChannel.alreadySet.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.logs.setLogChannel.alreadySet.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_log_channel_api(commandInfo.guild.id, channel.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.setLogChannel.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.logs.setLogChannel.success.description",
            channel=channel.mention,
        ),
    )
    await commandInfo.reply(embed=embed)
