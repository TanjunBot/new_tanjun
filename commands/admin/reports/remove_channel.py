import discord
from typing import Any, cast

import utility
from api import get_report_channel, remove_report_channel
from localizer import tanjunLocalizer


async def remove_channel(commandInfo: utility.commandInfo) -> None:
    if isinstance(commandInfo.user, discord.Member) and isinstance(commandInfo.channel, discord.abc.GuildChannel) and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.reports.remove_channel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.reports.remove_channel.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if not bool(await get_report_channel(commandInfo.guild.id)):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.remove_channel.noChannel.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.reports.remove_channel.noChannel.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_report_channel(commandInfo.guild.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.reports.remove_channel.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale), "commands.admin.reports.remove_channel.success.description"
        ),
    )
    await commandInfo.reply(embed=embed)
