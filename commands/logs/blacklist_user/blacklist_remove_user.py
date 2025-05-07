import discord

import utility
from api import (
    is_log_user_blacklisted as is_log_user_blacklisted_api,
)
from api import (
    remove_log_user_blacklist as remove_log_blacklist_user_api,
)
from localizer import tanjunLocalizer


async def blacklist_remove_user(commandInfo: utility.commandInfo, user: discord.Member):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveUser.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    isBlacklisted = await is_log_user_blacklisted_api(commandInfo.guild.id, user.id)

    if not isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveUser.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveUser.notBlacklisted.description",
            ),
        )
    else:
        await remove_log_blacklist_user_api(commandInfo.guild.id, user.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveUser.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistRemoveUser.success.description",
            ),
        )

    await commandInfo.reply(embed=embed)
