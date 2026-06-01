from locale_keys import locale
import discord
import utility
from services.giveaway_service import giveaway_service

async def remove_blacklist_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.remove_blacklist_role.missingPermission.title(command_info.locale), description=locale.commands.giveaway.remove_blacklist_role.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    blacklisted_roles = [role.entity_id for role in await giveaway_service.get_blacklisted_roles(str(command_info.guild.id))]
    if str(role.id) not in blacklisted_roles:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.remove_blacklist_role.notBlacklisted.title(command_info.locale), description=locale.commands.giveaway.remove_blacklist_role.notBlacklisted.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await giveaway_service.remove_blacklisted_role(guild_id=str(command_info.guild.id), role_id=str(role.id))
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.remove_blacklist_role.success.title(command_info.locale), description=locale.commands.giveaway.remove_blacklist_role.success.description(command_info.locale))
    await command_info.reply(embed=embed)