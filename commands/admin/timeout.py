from datetime import timedelta

import discord

import utility
from localizer import tanjunLocalizer
from utility import EmbedColor
from utils.checks import can_moderate, send_check_failure


async def timeout(
    command_info: utility.CommandInfo,
    member: discord.Member,
    duration: int | timedelta,
    reason: str | None = None,
) -> None:
    result = can_moderate(command_info, member, "moderate_members", "moderate_members")
    if await send_check_failure(command_info, "timeout", result):
        return

    try:
        if isinstance(duration, int):
            duration = timedelta(minutes=duration)

        if member.is_timed_out() is True:
            embed = utility.tanjunEmbed(
                colour=EmbedColor.WARNING,
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.alreadyTimedOut.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale), "commands.admin.timeout.alreadyTimedOut.description"
                ),
            )
            await command_info.reply(embed=embed)
            return

        await member.timeout(duration, reason=reason)
        embed = utility.tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.timeout.success.description",
                user=member.mention,
                duration=(
                    f"{int(duration.total_seconds() // 60)} minutes" if isinstance(duration, timedelta) else str(duration)
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.timeout.error.description"),
        )
        await command_info.reply(embed=embed)
