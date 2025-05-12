import discord

import utility
from api import (
    is_log_role_blacklisted as is_log_role_blacklisted_api,
)
from api import (
    remove_log_role_blacklist as remove_log_blacklist_role_api,
)
from localizer import tanjunLocalizer


async def blacklist_remove_role(commandInfo: utility.commandInfo, role: discord.Role):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    isBlacklisted = await is_log_role_blacklisted_api(commandInfo.guild.id, role.id)

    if not isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveRole.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveRole.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist_role_api(commandInfo.guild.id, role.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.logs.blacklistRemoveRole.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveRole.success.description",
            ),
        )

    await commandInfo.reply(embed=embed)
