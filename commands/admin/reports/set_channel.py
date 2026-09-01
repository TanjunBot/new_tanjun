from locale_keys import locale
import discord
import utility
from api import get_report_channel, set_report_channel

async def set_channel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_guild):
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.set_channel.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.reports.set_channel.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.set_channel.missingPermissionBot.title(command_info.locale), description=locale.commands.admin.reports.set_channel.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await get_report_channel(command_info.guild.id):
        embed = utility.tanjunEmbed(title=locale.commands.admin.reports.set_channel.alreadySet.title(str(command_info.locale)), description=locale.commands.admin.reports.set_channel.alreadySet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await set_report_channel(command_info.guild.id, channel.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.reports.set_channel.success.title(str(command_info.locale)), description=locale.commands.admin.reports.set_channel.success.description(str(command_info.locale)))
    await command_info.reply(embed=embed)