from locale_keys import locale
import discord
from api import set_wordchain_word
from utility import CommandInfo, tanjunEmbed

async def setwordchainchannel(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        return
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).moderate_members):
        embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.error.no_moderate_members_perms.title(command_info.locale), description=locale.minigames.setwordchainchannel.error.no_moderate_members_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if command_info.client.user is None:
        return
    self_member = command_info.guild.get_member(command_info.client.user.id)
    if self_member is None:
        return
    if not channel.permissions_for(self_member).send_messages:
        embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.error.no_send_perms.title(command_info.locale), description=locale.minigames.setwordchainchannel.error.no_send_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(self_member).manage_messages:
        embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.error.no_message_delete_perms.title(command_info.locale), description=locale.minigames.setwordchainchannel.error.no_message_delete_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(self_member).read_messages:
        embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.error.no_read_perms.title(command_info.locale), description=locale.minigames.setwordchainchannel.error.no_read_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(self_member).view_channel:
        embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.error.no_view_perms.title(command_info.locale), description=locale.minigames.setwordchainchannel.error.no_view_perms.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await set_wordchain_word(channel_id=channel.id, guild_id=command_info.guild.id, word='', worder_id='nobody')
    introduction_embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.introduction.title(str(command_info.locale)), description=locale.minigames.setwordchainchannel.introduction.description(str(command_info.locale)))
    await channel.send(embed=introduction_embed)
    embed = tanjunEmbed(title=locale.minigames.setwordchainchannel.success.title(str(command_info.locale)), description=locale.minigames.setwordchainchannel.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)