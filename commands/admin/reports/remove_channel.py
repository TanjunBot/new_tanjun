from locale_keys import locale
import discord
import utility
from api import get_report_channel, remove_report_channel

async def remove_channel(command_info: utility.CommandInfo) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_guild):
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.remove_channel.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.reports.remove_channel.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not bool(await get_report_channel(command_info.guild.id)):
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.remove_channel.noChannel.title(str(command_info.locale)), description=locale.commands.admin.reports.remove_channel.noChannel.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    await remove_report_channel(command_info.guild.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.reports.remove_channel.success.title(str(command_info.locale)), description=locale.commands.admin.reports.remove_channel.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)