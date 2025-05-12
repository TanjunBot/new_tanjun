import discord

import utility
from api import (
    add_log_blacklist_channel as add_log_blacklist_channel_api,
)
from api import (
    is_log_channel_blacklisted as is_log_channel_blacklisted_api,
)
from localizer import tanjunLocalizer


async def blacklist_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistChannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    isBlacklisted = await is_log_channel_blacklisted_api(commandInfo.guild.id, channel.id)

    if isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistChannel.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistChannel.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_channel_api(commandInfo.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistChannel.blacklisted.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistChannel.blacklisted.description",
            ),
        )

    await commandInfo.reply(embed=embed)
