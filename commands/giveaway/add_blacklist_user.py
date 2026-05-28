import discord

import utility
from services.giveaway_service import giveaway_service
from localizer import tanjunLocalizer


async def add_blacklist_user(
    command_info: utility.CommandInfo,
    user: discord.User,
) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await giveaway_service.is_user_blacklisted(str(command_info.guild.id), str(user.id)):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await giveaway_service.add_blacklisted_user(
        guild_id=str(command_info.guild.id),  # type: ignore[union-attr]
        user_id=str(user.id),
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.add_blacklist_user.success.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.add_blacklist_user.success.description",
        ),
    )

    await command_info.reply(embed=embed)
