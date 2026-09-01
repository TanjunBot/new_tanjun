from locale_keys import locale
import discord
import utility
from services.booster_service import BoosterType, booster_service
from utility import CommandInfo, tanjunEmbed

async def setupBoosterChannel(command_info: CommandInfo, category: discord.CategoryChannel) -> None:
    if isinstance(command_info.user, discord.User) or command_info.guild is None:
        embed = utility.tanjunEmbed(title=locale.errors.guildonly.title(command_info.locale), description=locale.errors.guildonly.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not getattr(command_info.user, 'guild_permissions', None) or not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(title=locale.commands.utility.setupboosterchannel.missingPermission.title(command_info.locale), description=locale.commands.utility.setupboosterchannel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    booster_channel = await booster_service.get(BoosterType.CHANNEL, str(command_info.guild.id))
    if booster_channel:
        embed = tanjunEmbed(title=locale.commands.utility.setupboosterchannel.already_set.title(command_info.locale), description=locale.commands.utility.setupboosterchannel.already_set.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await booster_service.add(BoosterType.CHANNEL, str(command_info.guild.id), str(category.id))
    embed = tanjunEmbed(title=locale.commands.utility.setupboosterchannel.success.title(str(command_info.locale)), description=locale.commands.utility.setupboosterchannel.success.description(command_info.locale))
    await command_info.reply(embed=embed)