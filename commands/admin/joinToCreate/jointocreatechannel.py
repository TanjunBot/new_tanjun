import discord
import utility
from localizer import tanjunLocalizer
from api import set_join_to_create_channel, get_join_to_create_channel


async def jointocreatechannel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.missingPermission.description")
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_join_to_create_channel(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.alreadySet.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.alreadySet.description")
        )
        await commandInfo.reply(embed=embed)
        return

    await set_join_to_create_channel(commandInfo.guild.id, channel.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.jointocreatechannel.success.description")
    )
    await commandInfo.reply(embed=embed)
