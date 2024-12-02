from api import remove_log_role_blacklist as remove_log_blacklist_role_api, is_log_role_blacklisted as is_log_role_blacklisted_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_remove_role(commandInfo: utility.commandInfo, role: discord.Role):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRemoveRole.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    isBlacklisted = await is_log_role_blacklisted_api(commandInfo.guild.id, role.id)

    if not isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveRole.notBlacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveRole.notBlacklisted.description")
        )
    else:
        await remove_log_blacklist_role_api(commandInfo.guild.id, role.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveRole.success.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveRole.success.description")
        )

    await commandInfo.reply(embed=embed) 