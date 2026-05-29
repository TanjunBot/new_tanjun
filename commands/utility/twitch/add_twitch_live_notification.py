import discord

from commands.utility.twitch.twitch_api import (
    get_uuid_by_twitch_name,
    subscribe_to_twitch_online_notification,
)
from localizer import tanjunLocalizer
from services.twitch_service import get_twitch_service
from utility import CommandInfo, tanjunEmbed


async def addTwitchLiveNotification(
    command_info: CommandInfo,
    twitch_name: str,
    channel: discord.TextChannel,
    notification_message: str | None = None,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.missingPermissions.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        not channel.permissions_for(command_info.guild.me).send_messages  # type: ignore[union-attr]
        and not channel.permissions_for(command_info.guild.me).embed_links  # type: ignore[union-attr]
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.missingBotPermissions.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    uuid = await get_uuid_by_twitch_name(twitch_name)
    if not uuid:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.twitch.addTwitchLiveNotification.error.twitchNameNotFound.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    service = get_twitch_service()
    if service is not None:
        await service.add_notification(
            str(command_info.guild.id),  # type: ignore[union-attr]
            str(channel.id),
            uuid,
            twitch_name,
            notification_message,
        )

    await subscribe_to_twitch_online_notification(uuid)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.twitch.addTwitchLiveNotification.success.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.twitch.addTwitchLiveNotification.success.description",
            twitch_name=twitch_name,
            channel=channel.mention,
        ),
    )
    await command_info.reply(embed=embed)
