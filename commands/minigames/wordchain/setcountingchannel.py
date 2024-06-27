from api import set_wordchain_word
from utility import commandInfo, checkIfHasPro, tanjunEmbed
from localizer import tanjunLocalizer
import discord

async def setwordchainchannel(commandInfo: commandInfo, channel: discord.TextChannel):
    
    if not commandInfo.user.guild_permissions.moderate_members:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_moderate_members_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_moderate_members_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not checkIfHasPro(commandInfo.guild.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_pro.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_pro.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    selfMember = commandInfo.guild.get_member(commandInfo.client.user.id)

    if not channel.permissions_for(selfMember).send_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_send_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_send_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).manage_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_message_delete_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_message_delete_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).read_messages:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_read_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_read_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(selfMember).view_channel:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_view_perms.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.error.no_view_perms.description"),
        )
        await commandInfo.reply(embed=embed)
        return
    
    set_wordchain_word(channel_id=channel.id, guild_id=commandInfo.guild.id, word="", worder_id="nobody")

    introductionEmbed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.modesintroduction.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.modesintroduction.description"),
    )
    await channel.send(embed=introductionEmbed)

    embed = tanjunEmbed(    
        title=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "minigames.setwordchainchannel.success.description", channel=channel.mention),
    )
    await commandInfo.reply(embed=embed)