import discord

import utility
from api import (
    add_log_blacklist_channel as add_log_blacklist_channel_api,
)
from api import (
    is_log_channel_blacklisted as is_log_channel_blacklisted_api,
)
from localizer import tanjunLocalizer


async def blacklist_channel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistChannel.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistChannel.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_channel_blacklisted_api(command_info.guild.id, channel.id)

    if is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistChannel.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistChannel.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_channel_api(command_info.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistChannel.blacklisted.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistChannel.blacklisted.description",
            ),
        )

    await command_info.reply(embed=embed)
