from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import set_twitch_online_notification
import discord
from commands.utility.twitch.twitchApi import get_uuid_by_twitch_name, subscribe_to_twitch_online_notification

async def addTwitchLiveNotification(commandInfo: commandInfo, twitch_name: str, channel: discord.TextChannel, notification_message: str = None):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).send_messages and not channel.permissions_for(commandInfo.guild.me).embed_links:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    uuid = await get_uuid_by_twitch_name(twitch_name)
    if not uuid:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_twitch_online_notification(commandInfo.guild.id, channel.id, uuid, twitch_name, notification_message)

    await subscribe_to_twitch_online_notification(uuid)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.utility.twitch.addTwitchLiveNotification.success.description", twitch_name=twitch_name, channel=channel.mention),
    )
    await commandInfo.reply(embed=embed)