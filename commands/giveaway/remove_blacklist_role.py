import discord

import utility
from api import (
    get_blacklisted_roles as get_giveaway_blacklisted_roles,
)
from api import (
    remove_giveaway_blacklisted_role as remove_blacklist_role_api,
)
from localizer import tanjunLocalizer


async def remove_blacklist_role(
    command_info: utility.CommandInfo,
    role: discord.Role,
) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_role.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_role.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    blacklisted_roles = [role.entity_id for role in await get_giveaway_blacklisted_roles(command_info.guild.id)]  # type: ignore[union-attr]

    if str(role.id) not in blacklisted_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_role.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.remove_blacklist_role.notBlacklisted.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_blacklist_role_api(
        guild_id=command_info.guild.id,  # type: ignore[union-attr]
        role_id=role.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.remove_blacklist_role.success.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.remove_blacklist_role.success.description",
        ),
    )
    await command_info.reply(embed=embed)
