from locale_keys import locale
import discord
from commands.utility.twitch.twitch_api import get_uuid_by_twitch_name, subscribe_to_twitch_online_notification
from services.twitch_service import get_twitch_service
from utility import CommandInfo, tanjunEmbed

async def addTwitchLiveNotification(command_info: CommandInfo, twitch_name: str, channel: discord.TextChannel, notification_message: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.title(command_info.locale), description=locale.commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(command_info.guild.me).send_messages and (not channel.permissions_for(command_info.guild.me).embed_links):
        embed = tanjunEmbed(title=locale.commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.title(command_info.locale), description=locale.commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    uuid = await get_uuid_by_twitch_name(twitch_name)
    if not uuid:
        embed = tanjunEmbed(title=locale.commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.title(command_info.locale), description=locale.commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    service = get_twitch_service()
    if service is None:
        embed = tanjunEmbed(title='Service Unavailable', description='Twitch service is not initialized.')
        await command_info.reply(embed=embed)
        return
    await service.add_notification(str(command_info.guild.id), str(channel.id), uuid, twitch_name, notification_message)
    await subscribe_to_twitch_online_notification(uuid)
    embed = tanjunEmbed(title=locale.commands.utility.twitch.addTwitchLiveNotification.success.title(command_info.locale), description=locale.commands.utility.twitch.addTwitchLiveNotification.success.description(command_info.locale, twitch_name=twitch_name, channel=channel.mention))
    await command_info.reply(embed=embed)