from api import add_log_blacklist_channel as add_log_blacklist_channel_api, remove_log_blacklist_channel as remove_log_blacklist_channel_api, is_log_channel_blacklisted as is_log_channel_blacklisted_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_remove_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistRemoveChannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    isBlacklisted = await is_log_channel_blacklisted_api(commandInfo.guild.id, channel.id)

    if not isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveChannel.notBlacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveChannel.notBlacklisted.description")
        )
    else:
        await add_log_blacklist_channel_api(commandInfo.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveChannel.success.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistRemoveChannel.success.description")
        )

    await commandInfo.reply(embed=embed)