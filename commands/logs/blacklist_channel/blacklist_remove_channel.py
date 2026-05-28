import discord

import utility
from api import (
    LogBlacklistTarget,
)
from api import (
    is_log_blacklisted as is_log_blacklisted_api,
)
from api import (
    remove_log_blacklist as remove_log_blacklist_api,
)
from localizer import tanjunLocalizer


async def blacklist_remove_channel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_blacklisted_api(LogBlacklistTarget.CHANNEL, command_info.guild.id, channel.id)

    if not is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist_api(LogBlacklistTarget.CHANNEL, command_info.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRemoveChannel.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveChannel.success.description",
            ),
        )

    await command_info.reply(embed=embed)
