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
        return

    selfMember = commandInfo.guild.get_member(commandInfo.client.user.id)

    if not channel.permissions_for(selfMember).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_send_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_send_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_message_delete_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_message_delete_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).read_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_read_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_read_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).view_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_view_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.error.no_view_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    set_counting_progress(channel_id=channel.id, guild_id=commandInfo.guild.id, progress=0)

    introductionEmbed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.introduction.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.introduction.description"),
    )
    await channel.send(embed=introductionEmbed)

    embed = tanjunEmbed(    
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setcountingchannel.success.description").format(channel.mention),
    )
    await commandInfo.reply(embed=embed)