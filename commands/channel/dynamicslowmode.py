import asyncio
import time
from collections import defaultdict, deque

import discord

import utility
from api import (
    add_dynamicslowmode,
    cash_slowmode_delay,
    get_dynamicslowmode,
    get_dynamicslowmode_channels,
    remove_cashed_slowmode_delay,
    remove_dynamicslowmode,
)
from localizer import tanjunLocalizer

# In-memory message tracking per channel
# Maps channel_id -> deque of timestamps (maxlen=100 to bound memory usage)
_recent_messages: dict[int, deque[float]] = defaultdict(lambda: deque(maxlen=100))
_recent_messages_lock = asyncio.Lock()


async def addDynamicslowmode(
    command_info: utility.CommandInfo,
    channel: discord.TextChannel,
    messages: int,
    per: int,
    resetafter: int = 60,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        not channel.permissions_for(command_info.guild.me).manage_messages  # type: ignore[union-attr]
        or not channel.permissions_for(command_info.guild.me).read_message_history  # type: ignore[union-attr]
        or not channel.permissions_for(command_info.guild.me).manage_channels  # type: ignore[union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingBotPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.alreadySet.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.alreadySet.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await add_dynamicslowmode(command_info.guild.id, channel.id, messages, per, resetafter)  # type: ignore[union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.channel.dynamicslowmode.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.channel.dynamicslowmode.success.description",
        ),
    )
    await command_info.reply(embed=embed)


async def removeDynamicslowmode(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.notSet.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.notSet.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_dynamicslowmode(command_info.guild.id, channel.id)  # type: ignore[union-attr]
    # Clean up in-memory tracking
    async with _recent_messages_lock:
        _recent_messages.pop(int(channel.id), None)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.channel.dynamicslowmode.deleteSuccess.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.channel.dynamicslowmode.deleteSuccess.description",
        ),
    )
    await command_info.reply(embed=embed)


async def getDynamicslowmode_channels(command_info: utility.CommandInfo) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    channels = await get_dynamicslowmode_channels(command_info.guild.id)  # type: ignore[union-attr]
    if not channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.noChannels.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.channel.dynamicslowmode.noChannels.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    description = ""
    for channel in channels:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.channel.dynamicslowmode.channels.description",
            channel_id=channel.channel_id,
            messages=channel.messages,
            per=channel.per,
            resetafter=channel.reset_after,
        )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.channel.dynamicslowmode.channels.title"),
        description=description,
    )
    await command_info.reply(embed=embed)


async def dynamicslowmodeMessage(message: discord.Message) -> None:
    """Track messages in-memory and adjust slowmode when thresholds are exceeded."""
    dynamic_slowmode_channel = await get_dynamicslowmode(message.channel.id)
    if not dynamic_slowmode_channel:
        return

    cashed_slowmode_delay = dynamic_slowmode_channel.cached_slowmode

    if not cashed_slowmode_delay:
        await cash_slowmode_delay(message.channel.id, message.channel.slowmode_delay)  # type: ignore[union-attr, arg-type]
        cashed_slowmode_delay = message.channel.slowmode_delay  # type: ignore[union-attr]

    channel_id: int = message.channel.id  # type: ignore[assignment]
    now = time.time()

    # Track in memory (protected by lock to avoid race conditions)
    async with _recent_messages_lock:
        _recent_messages[channel_id].append(now)

        # Count messages in the time window
        cutoff = now - dynamic_slowmode_channel.reset_after
        messages_in_window = sum(1 for t in _recent_messages[channel_id] if t > cutoff)

    reason_locale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.reason",
        messages=messages_in_window,
        per=dynamic_slowmode_channel.per,
    )
    reset_reason_locale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.resetReason",
    )

    new_slowmode = int(messages_in_window / dynamic_slowmode_channel.per)
    if new_slowmode != message.channel.slowmode_delay and new_slowmode > cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=new_slowmode, reason=reason_locale)  # type: ignore[union-attr]
    elif new_slowmode <= cashed_slowmode_delay and message.channel.slowmode_delay != cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=cashed_slowmode_delay, reason=reset_reason_locale)  # type: ignore[union-attr]
        await remove_cashed_slowmode_delay(message.channel.id)
