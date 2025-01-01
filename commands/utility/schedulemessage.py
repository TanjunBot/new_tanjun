import discord
import utility
from localizer import tanjunLocalizer
from datetime import datetime, timedelta
from api import (
    add_scheduled_message,
    get_user_scheduled_messages_in_timeframe,
    get_ready_scheduled_messages,
    remove_scheduled_message,
    update_scheduled_message_repeat_amount,
)
from typing import List


async def schedule_message(
    commandInfo: utility.commandInfo,
    content: str,
    send_in: str,
    channel: discord.TextChannel = None,
    repeat: str = None,
    repeat_amount: int = None,
    attachments: List[discord.Attachment] = None,
):
    # Parse send_in time
    try:
        send_time = utility.relativeTimeStrToDate(send_in)
    except ValueError:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.schedulemessage.invalidTime.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.schedulemessage.invalidTime.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check if time is in the future
    if send_time <= datetime.now():
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.utility.schedulemessage.pastTime.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.schedulemessage.pastTime.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    # Check permissions for channel messages
    if channel:
        # Check if user has permission to schedule repeating messages
        if repeat and not commandInfo.user.guild_permissions.manage_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noRepeatPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noRepeatPermission.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        # Check if user can send messages in channel
        if not channel.permissions_for(commandInfo.user).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noChannelPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noChannelPermission.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        # Check if bot can send messages in channel
        if not channel.permissions_for(commandInfo.guild.me).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noBotChannelPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noBotChannelPermission.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    else:
        dmChannel = await commandInfo.user.create_dm()
        if not dmChannel:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noDMPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noDMPermission.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return
        if not dmChannel.permissions_for(commandInfo.guild.me).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noDMPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.noDMPermission.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    # Check scheduling limits for non-moderators
    if channel and not commandInfo.user.guild_permissions.manage_messages:
        # Check if user has other messages scheduled within 1 hour
        start_time = send_time - timedelta(hours=1)
        end_time = send_time + timedelta(hours=1)
        existing_messages = await get_user_scheduled_messages_in_timeframe(
            commandInfo.user.id, start_time, end_time, commandInfo.guild.id
        )

        if existing_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.tooManyScheduled.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.schedulemessage.tooManyScheduled.description",
                ),
            )
            await commandInfo.reply(embed=embed)
            return

    # Schedule the message
    await add_scheduled_message(
        guild_id=commandInfo.guild.id if channel else None,
        channel_id=channel.id if channel else None,
        user_id=commandInfo.user.id,
        content=content,
        send_time=send_time,
        repeat_interval=utility.relativeTimeToSeconds(repeat) if repeat else None,
        repeat_amount=repeat_amount,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.utility.schedulemessage.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.schedulemessage.success.description",
            time=send_time.strftime("%Y-%m-%d %H:%M:%S"),
            channel=channel.mention if channel else "DM",
        ),
    )
    await commandInfo.reply(embed=embed)


async def send_scheduled_messages(client):
    """Send all scheduled messages that are ready to be sent"""
    ready_messages = await get_ready_scheduled_messages()

    for msg in ready_messages:
        try:
            # Extract message details
            message_id = msg[0]
            guild_id = int(msg[1]) if msg[1] else None
            channel_id = int(msg[2]) if msg[2] else None
            user_id = int(msg[3])
            content = msg[4]
            repeat_interval = msg[6]
            repeat_amount = msg[7]

            # Get the target channel or user
            if channel_id:
                guild = client.get_guild(guild_id)
                if not guild:
                    continue

                channel = guild.get_channel(channel_id)
                if not channel:
                    continue

                target = channel
            else:
                user = await client.fetch_user(user_id)
                if not user:
                    continue

                target = user

            # Send the message
            embed = utility.tanjunEmbed(description=content)
            await target.send(embed=embed)

            if repeat_amount and repeat_amount != 0:
                repeat_amount -= 1
                if repeat_amount == 0:
                    await remove_scheduled_message(message_id)
                else:
                    await update_scheduled_message_repeat_amount(
                        message_id, repeat_amount
                    )

            if not repeat_interval or not repeat_amount:
                await remove_scheduled_message(message_id)

        except Exception:
            pass
