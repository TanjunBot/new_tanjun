import discord

import utility
from api import check_if_reporter_is_blocked, unblock_reporter
from localizer import tanjunLocalizer


async def unblock_reporter_cmd(command_info: utility.CommandInfo, user: discord.Member) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_guild
    ):
        return await command_info.reply(  # type: ignore[return-value]
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.reports.unblock_reporter.missingPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.reports.unblock_reporter.missingPermission.description",
                ),
            )
        )

    assert command_info.guild is not None
    blocked_status = await check_if_reporter_is_blocked(command_info.guild.id, user.id)
    if not blocked_status:
        return await command_info.reply(  # type: ignore[return-value]
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.reports.unblock_reporter.notBlocked.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.reports.unblock_reporter.notBlocked.description",
                ),
            )
        )

    await unblock_reporter(command_info.guild.id, user.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.reports.unblock_reporter.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.reports.unblock_reporter.success.description",
        ),
    )
    await command_info.reply(embed=embed)
