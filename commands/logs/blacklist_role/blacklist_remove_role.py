import discord

import utility
from api import (
    LogBlacklistTarget,
    is_log_blacklisted as is_log_blacklisted_api,
    remove_log_blacklist as remove_log_blacklist_api,
)
from localizer import tanjunLocalizer


async def blacklist_remove_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    is_blacklisted = await is_log_blacklisted_api(LogBlacklistTarget.ROLE, command_info.guild.id, role.id)

    if not is_blacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveRole.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveRole.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist_api(LogBlacklistTarget.ROLE, command_info.guild.id, role.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.logs.blacklistRemoveRole.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.logs.blacklistRemoveRole.success.description",
            ),
        )

    await command_info.reply(embed=embed)
