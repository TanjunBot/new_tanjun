import discord

import utility
from localizer import tanjunLocalizer
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure


async def ban(
    command_info: utility.CommandInfo,
    target: discord.Member,
    reason: str | None = None,
    delete_message_days: int = 0,
) -> None:
    result = can_moderate(command_info, target, "ban_members", "ban_members")
    if await send_check_failure(command_info, "ban", result):
        return

    try:
        await target.ban(reason=reason, delete_message_days=delete_message_days)
        embed = utility.tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.ban.success.description",
                user=target.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.noReasonProvided")
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.error.description"),
        )
        await command_info.reply(embed=embed)
