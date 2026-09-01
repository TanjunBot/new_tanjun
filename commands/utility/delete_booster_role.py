from locale_keys import locale
import discord
import utility
from services.booster_service import BoosterType, booster_service
from utility import CommandInfo, tanjunEmbed

async def deleteBoosterRole(command_info: CommandInfo) -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(title=locale.errors.guildOnly.title(command_info.locale), description=locale.errors.guildOnly.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if command_info.channel is None:
        embed = utility.tanjunEmbed(title=locale.errors.noChannel.title(command_info.locale), description=locale.errors.noChannel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.utility.deleteboosterrole.missingPermission.title(command_info.locale), description=locale.commands.utility.deleteboosterrole.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    booster_role = await booster_service.get(BoosterType.ROLE, str(command_info.guild.id))
    if not booster_role:
        embed = tanjunEmbed(title=locale.commands.utility.deleteboosterrole.no_booster_role.title(command_info.locale), description=locale.commands.utility.deleteboosterrole.no_booster_role.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await booster_service.delete(BoosterType.ROLE, str(command_info.guild.id))
    embed = tanjunEmbed(title=locale.commands.utility.deleteboosterrole.success.title(str(command_info.locale)), description=locale.commands.utility.deleteboosterrole.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)