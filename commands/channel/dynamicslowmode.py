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


async def addDynamicslowmode(
    commandInfo: utility.CommandInfo,
    channel: discord.TextChannel,
    messages: int,
    per: int,
    resetafter: int = 60,
) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if (
        not channel.permissions_for(commandInfo.guild.me).manage_messages  # type: ignore[union-attr]
        or not channel.permissions_for(commandInfo.guild.me).read_message_history  # type: ignore[union-attr]
        or not channel.permissions_for(commandInfo.guild.me).manage_channels  # type: ignore[union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingBotPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.alreadySet.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.alreadySet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_dynamicslowmode(commandInfo.guild.id, channel.id, messages, per, resetafter)  # type: ignore[union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.channel.dynamicslowmode.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.channel.dynamicslowmode.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def removeDynamicslowmode(commandInfo: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.notSet.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.notSet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_dynamicslowmode(commandInfo.guild.id, channel.id)  # type: ignore[union-attr]
    # Clean up in-memory tracking
    _recent_messages.pop(int(channel.id), None)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.channel.dynamicslowmode.deleteSuccess.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.channel.dynamicslowmode.deleteSuccess.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def getDynamicslowmodeChannels(commandInfo: utility.CommandInfo) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    channels = await get_dynamicslowmode_channels(commandInfo.guild.id)  # type: ignore[union-attr]
    if not channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.noChannels.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.channel.dynamicslowmode.noChannels.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    description = ""
    for channel in channels:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.channel.dynamicslowmode.channels.description",
            channel_id=channel.channel_id,
            messages=channel.messages,
            per=channel.per,
            resetafter=channel.reset_after,
        )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.channel.dynamicslowmode.channels.title"),
        description=description,
    )
    await commandInfo.reply(embed=embed)


async def dynamicslowmodeMessage(message: discord.Message) -> None:
    """Track messages in-memory and adjust slowmode when thresholds are exceeded."""
    dynamicSlowmodeChannel = await get_dynamicslowmode(message.channel.id)
    if not dynamicSlowmodeChannel:
        return

    cashed_slowmode_delay = dynamicSlowmodeChannel.cached_slowmode

    if not cashed_slowmode_delay:
        await cash_slowmode_delay(message.channel.id, message.channel.slowmode_delay)  # type: ignore[union-attr, arg-type]
        cashed_slowmode_delay = message.channel.slowmode_delay  # type: ignore[union-attr]

    channel_id: int = message.channel.id  # type: ignore[assignment]
    now = time.time()

    # Track in memory
    _recent_messages[channel_id].append(now)

    # Count messages in the time window
    cutoff = now - dynamicSlowmodeChannel.reset_after
    messages_in_window = sum(1 for t in _recent_messages[channel_id] if t > cutoff)

    reasonLocale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.reason",
        messages=messages_in_window,
        per=dynamicSlowmodeChannel.per,
    )
    resetReasonLocale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.resetReason",
    )

    new_slowmode = int(messages_in_window / dynamicSlowmodeChannel.per)
    if new_slowmode != message.channel.slowmode_delay and new_slowmode > cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=new_slowmode, reason=reasonLocale)  # type: ignore[union-attr]
    elif new_slowmode <= cashed_slowmode_delay and message.channel.slowmode_delay != cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=cashed_slowmode_delay, reason=resetReasonLocale)  # type: ignore[union-attr]
        await remove_cashed_slowmode_delay(message.channel.id)
