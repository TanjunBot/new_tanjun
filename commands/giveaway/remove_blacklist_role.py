from api import (
    remove_giveaway_blacklisted_role as remove_blacklist_role_api,
    get_blacklisted_roles as get_giveaway_blacklisted_roles,
)
import discord
import utility
from localizer import tanjunLocalizer


async def remove_blacklist_role(
    commandInfo: utility.commandInfo,
    role: discord.Role,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_role.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_role.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    blacklistedRoles = [
        role[0] for role in await get_giveaway_blacklisted_roles(commandInfo.guild.id)
    ]

    if str(role.id) not in blacklistedRoles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_role.notBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.remove_blacklist_role.notBlacklisted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_blacklist_role_api(
        guild_id=commandInfo.guild.id,
        role_id=role.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.remove_blacklist_role.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.remove_blacklist_role.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
