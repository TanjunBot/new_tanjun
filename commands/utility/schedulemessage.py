from datetime import datetime, timedelta

import discord

import utility
from api import (
    add_scheduled_message,
    get_ready_scheduled_messages,
    get_user_scheduled_messages_in_timeframe,
    remove_scheduled_message,
    update_scheduled_message_repeat_amount,
)
from localizer import tanjunLocalizer


async def schedule_message(
    commandInfo: utility.commandInfo,
    content: str,
    send_in: str,
    channel: discord.TextChannel | None = None,
    repeat: str | None = None,
    repeat_amount: int | None = None,
    attachments: list[discord.Attachment] | None = None,
) -> None:
    if commandInfo.channel is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "errors.noChannel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    try:
        send_time = utility.relativeTimeStrToDate(send_in)
    except ValueError:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.schedulemessage.invalidTime.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.schedulemessage.invalidTime.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if send_time <= datetime.now():
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.schedulemessage.pastTime.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.schedulemessage.pastTime.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if channel:
        if (
            commandInfo.guild is not None
            and repeat
            and isinstance(commandInfo.user, discord.Member)
            and not commandInfo.channel.permissions_for(commandInfo.user).manage_messages
        ):
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

        if isinstance(commandInfo.user, discord.Member) and not channel.permissions_for(commandInfo.user).send_messages:
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

        if commandInfo.guild is not None and not channel.permissions_for(commandInfo.guild.me).send_messages:
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
        if commandInfo.guild is not None and not dmChannel.permissions_for(commandInfo.guild.me).send_messages:
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

    if (
        channel
        and commandInfo.guild is not None
        and isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_messages
    ):
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

    await add_scheduled_message(
        guild_id=commandInfo.guild.id if channel and commandInfo.guild else None,
        channel_id=channel.id if channel else None,
        user_id=commandInfo.user.id,
        content=content,
        send_time=send_time,
        repeat_interval=utility.relativeTimeToSeconds(repeat) if repeat else None,
        repeat_amount=repeat_amount,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.schedulemessage.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.schedulemessage.success.description",
            time=send_time.strftime("%Y-%m-%d %H:%M:%S"),
            channel=channel.mention if channel else "DM",
        ),
    )
    await commandInfo.reply(embed=embed)


async def send_scheduled_messages(client: discord.Client) -> None:
    """Send all scheduled messages that are ready to be sent"""
    ready_messages = await get_ready_scheduled_messages()

    if ready_messages is None:
        return

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

            target: (
                discord.VoiceChannel
                | discord.StageChannel
                | discord.ForumChannel
                | discord.TextChannel
                | discord.CategoryChannel
                | discord.DMChannel
            )

            if channel_id and guild_id:
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

                target = user.dm_channel if user.dm_channel else await user.create_dm()

            if isinstance(target, discord.CategoryChannel) or isinstance(target, discord.ForumChannel):
                return

            embed = utility.tanjunEmbed(description=content)
            await target.send(content=content, embed=embed)

            if repeat_amount and repeat_amount != 0:
                repeat_amount -= 1
                if repeat_amount == 0:
                    await remove_scheduled_message(message_id)
                else:
                    await update_scheduled_message_repeat_amount(message_id, repeat_amount)

            if not repeat_interval or not repeat_amount:
                await remove_scheduled_message(message_id)

        except Exception:
            pass
