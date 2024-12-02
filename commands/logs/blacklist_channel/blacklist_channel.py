from api import add_log_blacklist_channel as add_log_blacklist_channel_api, remove_log_blacklist_channel as remove_log_blacklist_channel_api, is_log_channel_blacklisted as is_log_channel_blacklisted_api
import utility
import discord
from localizer import tanjunLocalizer

async def blacklist_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistChannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.logs.blacklistChannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    isBlacklisted = await is_log_channel_blacklisted_api(commandInfo.guild.id, channel.id)

    if isBlacklisted:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistChannel.alreadyBlacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistChannel.alreadyBlacklisted.description")
        )
    else:
        await add_log_blacklist_channel_api(commandInfo.guild.id, channel.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistChannel.blacklisted.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.logs.blacklistChannel.blacklisted.description")
        )

    await commandInfo.reply(embed=embed)