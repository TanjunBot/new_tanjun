from api import remove_giveaway_blacklisted_user as remove_blacklist_user_api, get_giveaway_blacklisted_user
import discord
import utility
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
        return embed

    blacklistedUsers = [user[0] for user in get_giveaway_blacklisted_user(commandInfo.guild.id)]

    if str(user.id) not in blacklistedUsers:
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
        return embed

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
    return embed