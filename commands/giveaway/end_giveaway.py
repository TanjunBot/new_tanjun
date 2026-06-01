from locale_keys import locale
import utility
from commands.giveaway.utility import endGiveaway
from services.giveaway_service import giveaway_service

async def end_giveaway(command_info: utility.CommandInfo, giveaway_id: int) -> None:
    if not command_info.permissions.manage_guild:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.error.missingPermission.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.error.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    giveaway = await giveaway_service.get(giveaway_id)
    if not giveaway:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.error.notFound.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.error.notFound.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if giveaway.guild_id != str(command_info.guild.id):
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.error.notFound.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.error.notFound.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if giveaway.ended:
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.error.alreadyEnded.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.error.alreadyEnded.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not giveaway.started:
        await giveaway_service.delete(giveaway_id)
        embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.deleted.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.deleted.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await endGiveaway(giveaway_id, command_info.client)
    embed = utility.tanjunEmbed(title=locale.commands.giveaway.end_giveaway_command.success.title(command_info.locale), description=locale.commands.giveaway.end_giveaway_command.success.description(command_info.locale))
    await command_info.reply(embed=embed)