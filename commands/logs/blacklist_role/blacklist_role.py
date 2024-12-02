from api import add_log_role_blacklist as add_log_blacklist_role_api, is_log_role_blacklisted as is_log_role_blacklisted_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_role(commandInfo: utility.commandInfo, role: discord.Role):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRole.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRole.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    isBlacklisted = await is_log_role_blacklisted_api(commandInfo.guild.id, role.id)

    if isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRole.alreadyBlacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRole.alreadyBlacklisted.description")
        )
    else:
        await add_log_blacklist_role_api(commandInfo.guild.id, role.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRole.blacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRole.blacklisted.description")
        )

    await commandInfo.reply(embed=embed) 