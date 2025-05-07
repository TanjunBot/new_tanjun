import discord

import utility
from api import check_if_reporter_is_blocked, unblock_reporter
from localizer import tanjunLocalizer


async def unblock_reporter_cmd(commandInfo: utility.commandInfo, user: discord.Member):
    if not commandInfo.user.guild_permissions.manage_guild:
        return await commandInfo.reply(
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

    if not await check_if_reporter_is_blocked(commandInfo.guild.id, user.id):
        return await commandInfo.reply(
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
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.unblock_reporter.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.reports.unblock_reporter.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)
