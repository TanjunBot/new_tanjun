import discord
import utility
from localizer import tanjunLocalizer
from api import remove_report_channel, get_report_channel

async def remove_channel(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.reports.remove_channel.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.reports.remove_channel.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if not await get_report_channel(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.remove_channel.noChannel.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.remove_channel.noChannel.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_report_channel(commandInfo.guild.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.remove_channel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.reports.remove_channel.success.description"),
    )
    await commandInfo.reply(embed=embed)
