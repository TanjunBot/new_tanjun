from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import set_levelup_channel
import discord


async def set_levelup_channel_command(
    commandInfo: commandInfo, channel: discord.TextChannel = None
):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setlevelupchannel.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setlevelupchannel.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if channel:
        await set_levelup_channel(str(commandInfo.guild.id), str(channel.id))
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setlevelupchannel.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setlevelupchannel.success.description",
                channel=channel.mention,
            ),
        )
    else:
        await set_levelup_channel(str(commandInfo.guild.id), None)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setlevelupchannel.reset.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.level.setlevelupchannel.reset.description"
            ),
        )

    await commandInfo.reply(embed=embed)
