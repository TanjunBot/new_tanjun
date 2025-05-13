import discord

from api import set_levelup_channel
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def set_levelup_channel_command(commandInfo: commandInfo, channel: discord.TextChannel = None):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
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
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.setlevelupchannel.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setlevelupchannel.success.description",
                channel=channel.mention,
            ),
        )
    else:
        await set_levelup_channel(str(commandInfo.guild.id), None)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.setlevelupchannel.reset.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.level.setlevelupchannel.reset.description"
            ),
        )

    await commandInfo.reply(embed=embed)
