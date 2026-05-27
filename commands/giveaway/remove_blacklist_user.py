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
    command_info: utility.CommandInfo,
    user: discord.User,
) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_user.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_user.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await check_if_user_blacklisted(command_info.guild.id, user.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_user.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_user.notBlacklisted.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_blacklist_user_api(
        guild_id=command_info.guild.id,  # type: ignore[union-attr]
        user_id=user.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.remove_blacklist_user.success.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.remove_blacklist_user.success.description",
        ),
    )
    await command_info.reply(embed=embed)
