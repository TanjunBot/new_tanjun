import discord  # type: ignore[import-not-found]

import utility
from api import check_if_reporter_is_blocked, unblock_reporter
from localizer import tanjunLocalizer


async def unblock_reporter_cmd(commandInfo: utility.CommandInfo, user: discord.Member) -> None:  # type: ignore[no-any-unimported]
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild
    ):
        return await commandInfo.reply(  # type: ignore[no-any-return]
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.unblock_reporter.missingPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.unblock_reporter.missingPermission.description",
                ),
            )
        )

    assert commandInfo.guild is not None
    blocked_status = await check_if_reporter_is_blocked(commandInfo.guild.id, user.id)
    if blocked_status is None or len(blocked_status) == 0:
        return await commandInfo.reply(  # type: ignore[no-any-return]
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.unblock_reporter.notBlocked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.reports.unblock_reporter.notBlocked.description",
                ),
            )
        )

    await unblock_reporter(commandInfo.guild.id, user.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.unblock_reporter.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.reports.unblock_reporter.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
