import discord

import utility
from api import get_report_channel, set_report_channel
from localizer import tanjunLocalizer


async def set_channel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_guild
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.reports.set_channel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.reports.set_channel.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.reports.set_channel.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.reports.set_channel.missingPermissionBot.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await get_report_channel(command_info.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.reports.set_channel.alreadySet.title"),
            description=tanjunLocalizer.localize(
                command_info.locale, "commands.admin.reports.set_channel.alreadySet.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    await set_report_channel(command_info.guild.id, channel.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.reports.set_channel.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.admin.reports.set_channel.success.description"
        ),
    )
    await command_info.reply(embed=embed)
