import discord

import utility
from api import get_report_channel, remove_report_channel
from localizer import tanjunLocalizer


async def remove_channel(command_info: utility.CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_guild
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.reports.remove_channel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.reports.remove_channel.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not bool(await get_report_channel(command_info.guild.id)):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.reports.remove_channel.noChannel.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.reports.remove_channel.noChannel.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_report_channel(command_info.guild.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.reports.remove_channel.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.admin.reports.remove_channel.success.description"
        ),
    )
    await command_info.reply(embed=embed)
