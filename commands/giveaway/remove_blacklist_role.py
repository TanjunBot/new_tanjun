from api import remove_giveaway_blacklisted_role as remove_blacklist_role_api
import discord
import utility
from localizer import tanjunLocalizer

def remove_blacklist_role(
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
        return embed

    if role not in commandInfo.guild.blacklist_roles:
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
        return embed

    remove_blacklist_role_api(
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
    return embed