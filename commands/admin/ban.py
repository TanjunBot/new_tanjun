from locale_keys import locale
import discord
import utility
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure

async def ban(command_info: utility.CommandInfo, target: discord.Member, reason: str | None=None, delete_message_days: int=0) -> None:
    result = can_moderate(command_info, target, 'ban_members', 'ban_members')
    if await send_check_failure(command_info, 'ban', result):
        return
    try:
        await target.ban(reason=reason, delete_message_days=delete_message_days)
        embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.admin.ban.success.title(str(command_info.locale)), description=locale.commands.admin.ban.success.description(command_info.locale, user=target.name, reason=reason if reason else locale.commands.admin.ban.noReasonProvided(str(command_info.locale))))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.ban.forbidden.title(str(command_info.locale)), description=locale.commands.admin.ban.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.ban.error.title(str(command_info.locale)), description=locale.commands.admin.ban.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)