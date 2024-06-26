from api import set_counting_progress, get_counting_channel_amount
from utility import commandInfo, checkIfHasPro, tanjunEmbed
from localizer import tanjunLocalizer
import discord

async def setCountingChannel(commandInfo: commandInfo, channel: discord.TextChannel):

    if get_counting_channel_amount(commandInfo.guild.id) != 0 and not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_pro_title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_pro_description"),
        )
        await commandInfo.reply(embed=embed)

    set_counting_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)

    embed = tanjunEmbed(    
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.success.description").format(channel.mention),
    )
    await commandInfo.reply(embed=embed)