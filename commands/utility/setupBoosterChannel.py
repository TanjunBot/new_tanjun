from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_booster_channel, add_booster_channel
import utility
import discord

async def setupBoosterChannel(commandInfo: commandInfo, category: discord.CategoryChannel):
    if not commandInfo.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale,
                "commands.utility.setupboosterchannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale,
                "commands.utility.setupboosterchannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return 
    
    booster_channel = await get_booster_channel(commandInfo.guild.id)
    if booster_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.already_set.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.setupboosterchannel.already_set.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_booster_channel(commandInfo.guild.id, category.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.setupboosterchannel.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.setupboosterchannel.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)
