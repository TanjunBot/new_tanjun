from api import add_giveaway_blacklisted_user as add_blacklist_user_api, get_giveaway_blacklisted_user
import discord
import utility
from localizer import tanjunLocalizer

async def add_blacklist_user(
    commandInfo: utility.commandInfo,
    user: discord.User,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.description",
            ),
        )
        return embed
    
    blacklistedUsers = [user[0] for user in get_giveaway_blacklisted_user(commandInfo.guild.id)]

    if str(user.id) in blacklistedUsers:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.description",
            ),
        )
        return embed

    await add_blacklist_user_api(
        guild_id=commandInfo.guild.id,
        user_id=user.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.add_blacklist_user.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.add_blacklist_user.success.description",
        ),
    )
    return embed