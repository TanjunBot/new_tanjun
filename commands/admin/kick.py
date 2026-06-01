from locale_keys import locale
import discord
import utility
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure

async def kick(command_info: utility.CommandInfo, target: discord.Member, reason: str | None=None) -> None:
    result = can_moderate(command_info, target, 'kick_members', 'kick_members')
    if await send_check_failure(command_info, 'kick', result):
        return
    try:
        await target.kick(reason=reason)
        embed = utility.tanjunEmbed(colour=EmbedColor.SUCCESS, title=locale.commands.admin.kick.success.title(str(command_info.locale)), description=locale.commands.admin.kick.success.description(command_info.locale, user=target.name, reason=reason if reason else locale.commands.admin.kick.noReasonProvided(str(command_info.locale))))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.kick.forbidden.title(str(command_info.locale)), description=locale.commands.admin.kick.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(colour=EmbedColor.ERROR, title=locale.commands.admin.kick.error.title(str(command_info.locale)), description=locale.commands.admin.kick.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)