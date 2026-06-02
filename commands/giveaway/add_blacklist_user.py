from locale_keys import locale
import discord
import utility
from services.giveaway_service import giveaway_service

async def add_blacklist_user(command_info: utility.CommandInfo, user: discord.User) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.add_blacklist_user.missingPermission.title(command_info.locale), description=locale.commands.giveaway.add_blacklist_user.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await giveaway_service.is_user_blacklisted(str(command_info.guild.id), str(user.id)):
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.add_blacklist_user.alreadyBlacklisted.title(command_info.locale), description=locale.commands.giveaway.add_blacklist_user.alreadyBlacklisted.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await giveaway_service.add_blacklisted_user(guild_id=str(command_info.guild.id), user_id=str(user.id))
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.add_blacklist_user.success.title(command_info.locale), description=locale.commands.giveaway.add_blacklist_user.success.description(command_info.locale))
    await command_info.reply(embed=embed)