import discord

import utility
from api import (
    check_if_user_blacklisted,
)
from api import (
    remove_giveaway_blacklisted_user as remove_blacklist_user_api,
)
from localizer import tanjunLocalizer


async def remove_blacklist_user(
    commandInfo: utility.commandInfo,
    user: discord.User,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_user.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_user.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await check_if_user_blacklisted(commandInfo.guild.id, user.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_user.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_user.notBlacklisted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_blacklist_user_api(
        guild_id=commandInfo.guild.id,
        user_id=user.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.remove_blacklist_user.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.remove_blacklist_user.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
