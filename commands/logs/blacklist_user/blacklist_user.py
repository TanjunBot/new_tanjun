from api import (
    get_log_user_blacklist as add_log_blacklist_user_api,
    is_log_user_blacklisted as is_log_user_blacklisted_api,
)
import utility
import discord
from localizer import tanjunLocalizer


async def blacklist_user(commandInfo: utility.commandInfo, user: discord.Member):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    isBlacklisted = await is_log_user_blacklisted_api(commandInfo.guild.id, user.id)

    if isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.alreadyBlacklisted.description",
            ),
        )
    else:
        await add_log_blacklist_user_api(commandInfo.guild.id, user.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.logs.blacklistUser.blacklisted.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.logs.blacklistUser.blacklisted.description",
            ),
        )

    await commandInfo.reply(embed=embed)
