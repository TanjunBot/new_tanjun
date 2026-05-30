import discord

import utility
from localizer import tanjunLocalizer
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure


async def kick(command_info: utility.CommandInfo, target: discord.Member, reason: str | None = None) -> None:
    result = can_moderate(command_info, target, "kick_members", "kick_members")
    if await send_check_failure(command_info, "kick", result):
        return

    try:
        await target.kick(reason=reason)
        embed = utility.tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.kick.success.description",
                user=target.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.noReasonProvided")
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.error.description"),
        )
        await command_info.reply(embed=embed)
