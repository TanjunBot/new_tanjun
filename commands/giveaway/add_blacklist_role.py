import discord

import utility
from api import (
    add_giveaway_blacklisted_role as add_blacklist_role_api,
)
from api import (
    get_blacklisted_roles as get_giveaway_blacklisted_roles,
)
from localizer import tanjunLocalizer


async def add_blacklist_role(
    command_info: utility.CommandInfo,
    role: discord.Role,
) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_role.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_role.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    blacklisted_roles = [role.entity_id for role in await get_giveaway_blacklisted_roles(command_info.guild.id)]  # type: ignore[union-attr]

    if str(role.id) in blacklisted_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_role.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.add_blacklist_role.alreadyBlacklisted.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await add_blacklist_role_api(command_info.guild.id, role.id)  # type: ignore[union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.giveaway.add_blacklist_role.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.add_blacklist_role.success.description",
        ),
    )
    await command_info.reply(embed=embed)
    return
