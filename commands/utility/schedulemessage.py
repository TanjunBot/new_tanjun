import io
import json
import logging
from datetime import datetime, timedelta

import aiohttp
import discord

import utility
from localizer import tanjunLocalizer
from services.scheduled_message_service import (
    Attachment,
    ScheduledMessageService,
    ScheduleMessageParams,
)


async def schedule_message(
    command_info: utility.CommandInfo,
    content: str,
    send_in: str,
    channel: discord.TextChannel | None = None,
    repeat: str | None = None,
    repeat_amount: int | None = None,
    attachments: list[discord.Attachment] | None = None,
) -> None:
    if command_info.channel is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return
    try:
        send_time = utility.relativeTimeStrToDate(send_in)
    except ValueError:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.schedulemessage.invalidTime.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.schedulemessage.invalidTime.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if send_time <= datetime.now():
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.schedulemessage.pastTime.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.schedulemessage.pastTime.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if channel:
        if (
            command_info.guild is not None
            and repeat is not None
            and isinstance(command_info.user, discord.Member)
            and not command_info.channel.permissions_for(command_info.user).manage_messages
        ):
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noRepeatPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noRepeatPermission.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

        if isinstance(command_info.user, discord.Member) and not channel.permissions_for(command_info.user).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noChannelPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noChannelPermission.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

        if command_info.guild is not None and not channel.permissions_for(command_info.guild.me).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noBotChannelPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noBotChannelPermission.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

    else:
        dm_channel = await command_info.user.create_dm()
        if command_info.guild is not None and not dm_channel.permissions_for(command_info.guild.me).send_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noDMPermission.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.noDMPermission.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

    if (
        channel
        and command_info.guild is not None
        and isinstance(command_info.user, discord.Member)
        and not command_info.channel.permissions_for(command_info.user).manage_messages
    ):
        start_time = send_time - timedelta(hours=1)
        end_time = send_time + timedelta(hours=1)
        existing_messages = await ScheduledMessageService.get_upcoming(
            user_id=str(command_info.user.id),
            start_time=start_time,
            end_time=end_time,
            guild_id=str(command_info.guild.id),
        )

        if existing_messages:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.tooManyScheduled.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.utility.schedulemessage.tooManyScheduled.description",
                ),
            )
            await command_info.reply(embed=embed)
            return

    # Convert Discord attachments to our Attachment model if provided
    attachment_models = None
    if attachments:
        attachment_models = [
            Attachment(
                filename=att.filename,
                content_type=att.content_type,
                size=att.size,
                url=att.url,
            )
            for att in attachments
        ]

    params = ScheduleMessageParams(
        guild_id=str(command_info.guild.id) if channel and command_info.guild else None,
        channel_id=str(channel.id) if channel else None,
        user_id=str(command_info.user.id),
        content=content,
        send_time=send_time,
        repeat_interval=utility.relativeTimeToSeconds(repeat) if repeat else None,
        repeat_amount=repeat_amount,
        attachments=attachment_models,
    )
    await ScheduledMessageService.schedule(params)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.schedulemessage.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.schedulemessage.success.description",
            time=send_time.strftime("%Y-%m-%d %H:%M:%S"),
            channel=channel.mention if channel else "DM",
        ),
    )
    await command_info.reply(embed=embed)


async def send_scheduled_messages(client: discord.Client) -> None:
    """Send all scheduled messages that are ready to be sent"""
    ready_messages = await ScheduledMessageService.get_due_messages()

    if ready_messages is None:
        return

    for msg in ready_messages:
        try:
            # Extract message details
            message_id = msg.message_id
            guild_id = int(msg.guild_id) if msg.guild_id else None
            channel_id = int(msg.channel_id) if msg.channel_id else None
            user_id = int(msg.user_id)
            content = msg.content
            repeat_interval = msg.repeat_interval
            repeat_amount = msg.repeat_amount

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
                try:
                    user = await client.fetch_user(user_id)
                except discord.NotFound:
                    continue

                target = user.dm_channel if user.dm_channel else await user.create_dm()

            if isinstance(target, (discord.CategoryChannel, discord.ForumChannel)):
                return

            # Parse and send attachments if present
            files: list[discord.File] = []
            if msg.attachments:
                try:
                    attachment_data: list[dict] = json.loads(msg.attachments)
                    for att_data in attachment_data:
                        url = att_data.get("url", "")
                        filename = att_data.get("filename", "file")

                        async with aiohttp.ClientSession() as session, session.get(url) as resp:
                            if resp.status == 200:
                                file_bytes = await resp.read()
                                files.append(
                                    discord.File(
                                        io.BytesIO(file_bytes),
                                        filename=filename,
                                    )
                                )
                except (json.JSONDecodeError, Exception):
                    logging.exception("Failed to parse attachments for scheduled message %s", message_id)

            embed = utility.tanjunEmbed(description=content)
            send_kwargs: dict = {"content": content, "embed": embed}
            if files:
                send_kwargs["files"] = files
            await target.send(**send_kwargs)

            if repeat_amount and repeat_amount != 0:
                repeat_amount -= 1
                if repeat_amount == 0:
                    await ScheduledMessageService.cancel(message_id)
                else:
                    await ScheduledMessageService.update_repeat(message_id, repeat_amount)

            if not repeat_interval or not repeat_amount:
                await ScheduledMessageService.cancel(message_id)

        except Exception:
            logging.exception("Failed to send scheduled message %s", message_id)
