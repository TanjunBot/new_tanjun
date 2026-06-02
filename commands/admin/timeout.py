from locale_keys import locale
from datetime import timedelta
import discord
import utility
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure

async def timeout(command_info: utility.CommandInfo, member: discord.Member, duration: int | timedelta, reason: str | None=None) -> None:
    result = can_moderate(command_info, member, 'moderate_members', 'moderate_members')
    if await send_check_failure(command_info, 'timeout', result):
        return
    try:
        if isinstance(duration, int):
            duration = timedelta(minutes=duration)
        if member.is_timed_out() is True:
            embed = utility.tanjunEmbed(colour=EmbedColor.WARNING, title=locale.commands.admin.timeout.alreadyTimedOut.title(str(command_info.locale)), description=locale.commands.admin.timeout.alreadyTimedOut.description(str(command_info.locale)))
            await command_info.reply(embed=embed)
            return
        await member.timeout(duration, reason=reason)
        embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.admin.timeout.success.title(str(command_info.locale)), description=locale.commands.admin.timeout.success.description(command_info.locale, user=member.mention, duration=f'{int(duration.total_seconds() // 60)} minutes' if isinstance(duration, timedelta) else str(duration)))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.timeout.forbidden.title(str(command_info.locale)), description=locale.commands.admin.timeout.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.timeout.error.title(str(command_info.locale)), description=locale.commands.admin.timeout.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)