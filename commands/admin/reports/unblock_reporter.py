from locale_keys import locale
import discord
import utility
from api import check_if_reporter_is_blocked, unblock_reporter

async def unblock_reporter_cmd(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_guild):
        return await command_info.reply(embed=utility.tanjunEmbed(title=locale.commands.admin.reports.unblock_reporter.missingPermission.title(command_info.locale), description=locale.commands.admin.reports.unblock_reporter.missingPermission.description(command_info.locale)))
    assert command_info.guild is not None
    blocked_status = await check_if_reporter_is_blocked(command_info.guild.id, user.id)
    if not blocked_status:
        return await command_info.reply(embed=utility.tanjunEmbed(title=locale.commands.admin.reports.unblock_reporter.notBlocked.title(command_info.locale), description=locale.commands.admin.reports.unblock_reporter.notBlocked.description(command_info.locale)))
    await unblock_reporter(command_info.guild.id, user.id)
    embed = utility.tanjunEmbed(title=locale.commands.admin.reports.unblock_reporter.success.title(str(command_info.locale)), description=locale.commands.admin.reports.unblock_reporter.success.description(command_info.locale))
    await command_info.reply(embed=embed)