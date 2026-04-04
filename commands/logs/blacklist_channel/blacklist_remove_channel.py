import discord  # type: ignore[import-not-found]

import utility
from api import (
    add_log_blacklist_channel as add_log_blacklist_channel_api,
)
from api import (
    is_log_channel_blacklisted as is_log_channel_blacklisted_api,
)
from localizer import tanjunLocalizer


async def blacklist_remove_channel(commandInfo: utility.CommandInfo, channel: discord.TextChannel) -> None:  # type: ignore[no-any-unimported]
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    isBlacklisted = await is_log_channel_blacklisted_api(commandInfo.guild.id, channel.id)

    if not isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_channel_api(commandInfo.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistRemoveChannel.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.success.description",
            ),
        )

    await commandInfo.reply(embed=embed)
