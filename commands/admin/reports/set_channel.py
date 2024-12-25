import discord
import utility
from localizer import tanjunLocalizer
from api import set_report_channel, get_report_channel


async def set_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if not commandInfo.user.guild_permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.set_channel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.reports.set_channel.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.set_channel.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.reports.set_channel.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_report_channel(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.set_channel.alreadySet.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.set_channel.alreadySet.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_report_channel(commandInfo.guild.id, channel.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.set_channel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.set_channel.success.description"),
    )
    await commandInfo.reply(embed=embed)
