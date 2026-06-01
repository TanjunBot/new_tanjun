from locale_keys import locale
import utility
from services.giveaway_service import giveaway_service

async def list_blacklist(command_info: utility.CommandInfo) -> None:
    if not command_info.permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.list_blacklist.missingPermission.title(command_info.locale), description=locale.commands.giveaway.list_blacklist.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    blacklisted_roles = [role.entity_id for role in await giveaway_service.get_blacklisted_roles(str(command_info.guild.id))]
    blacklisted_users = [user.entity_id for user in await giveaway_service.get_blacklisted_users(str(command_info.guild.id))]
    if len(blacklisted_roles) == 0 and len(blacklisted_users) == 0:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.list_blacklist.noBlacklist.title(command_info.locale), description=locale.commands.giveaway.list_blacklist.noBlacklist.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.list_blacklist.title(command_info.locale), description=locale.commands.giveaway.list_blacklist.description(command_info.locale))
    if blacklisted_roles:
        embed.add_field(name=locale.commands.giveaway.list_blacklist.roles(command_info.locale), value='\n'.join([f'<@&{role}>' for role in blacklisted_roles]), inline=False)
    if blacklisted_users:
        embed.add_field(name=locale.commands.giveaway.list_blacklist.users(command_info.locale), value='\n'.join([f'<@{user}>' for user in blacklisted_users]), inline=False)
    await command_info.reply(embed=embed)