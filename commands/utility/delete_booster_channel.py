from locale_keys import locale
import discord
import utility
from services.booster_service import BoosterType, booster_service
from utility import CommandInfo, tanjunEmbed

async def deleteBoosterChannel(command_info: CommandInfo) -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(title=locale.errors.guildOnly.title(command_info.locale), description=locale.errors.guildOnly.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if command_info.channel is None:
        embed = utility.tanjunEmbed(title=locale.errors.noChannel.title(command_info.locale), description=locale.errors.noChannel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = utility.tanjunEmbed(title=locale.commands.utility.deleteboosterchannel.missingPermission.title(command_info.locale), description=locale.commands.utility.deleteboosterchannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    booster_channel = await booster_service.get(BoosterType.CHANNEL, str(command_info.guild.id))
    if not booster_channel:
        embed = tanjunEmbed(title=locale.commands.utility.deleteboosterchannel.no_booster_channel.title(command_info.locale), description=locale.commands.utility.deleteboosterchannel.no_booster_channel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await booster_service.delete(BoosterType.CHANNEL, str(command_info.guild.id), entity_id=booster_channel)
    embed = tanjunEmbed(title=locale.commands.utility.deleteboosterchannel.success.title(str(command_info.locale)), description=locale.commands.utility.deleteboosterchannel.success.description(command_info.locale))
    await command_info.reply(embed=embed)