"""Dynamic slowmode commands — manage per-channel adaptive slowmode."""


import time

import discord

import utility
from localizer import tanjunLocalizer
from services.dynamicslowmode import DynamicSlowmodeService

# Shared service instance
_ds_service = DynamicSlowmodeService()


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

    if await _ds_service.get_config(str(channel.id)):
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

    await _ds_service.configure(
        str(command_info.guild.id), str(channel.id), messages, per, resetafter
    )  # type: ignore[union-attr]
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

    if not await _ds_service.get_config(str(channel.id)):
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

    await _ds_service.remove(str(command_info.guild.id), str(channel.id))  # type: ignore[union-attr]

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

    channels = await _ds_service.get_all_configs(str(command_info.guild.id))  # type: ignore[union-attr]
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
    for config in channels:
        description += tanjunLocalizer.localize(
            command_info.locale,
            "commands.channel.dynamicslowmode.channels.description",
            channel_id=config.channel_id,
            messages=config.messages,
            per=config.per,
            resetafter=config.reset_after,
        )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.channel.dynamicslowmode.channels.title"),
        description=description,
    )
    await command_info.reply(embed=embed)


async def dynamicslowmodeMessage(message: discord.Message) -> None:
    """Track messages in-memory and adjust slowmode when thresholds are exceeded."""
    config = await _ds_service.get_config(str(message.channel.id))
    if not config:
        return

    cashed_slowmode_delay = config.cached_slowmode

    if cashed_slowmode_delay is None:
        await _ds_service.cache_current_slowmode(
            str(message.channel.id), message.channel.slowmode_delay  # type: ignore[union-attr]
        )
        cashed_slowmode_delay = message.channel.slowmode_delay  # type: ignore[union-attr]

    now = time.time()

    # Track in memory via service
    channel_id: int = message.channel.id  # type: ignore[assignment]

    # Prune old timestamps before appending
    cutoff = now - config.reset_after
    while _ds_service._recent_messages[channel_id] and _ds_service._recent_messages[channel_id][0] <= cutoff:
        _ds_service._recent_messages[channel_id].popleft()

    _ds_service._recent_messages[channel_id].append(now)

    # Count messages in the time window
    messages_in_window = len(_ds_service._recent_messages[channel_id])

    reason_locale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.reason",
        messages=messages_in_window,
        per=config.per,
    )
    reset_reason_locale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.resetReason",
    )

    # Check if throttling is needed based on config threshold
    if messages_in_window > config.messages:
        # Calculate new slowmode: excess messages scaled by the per interval
        new_slowmode = int((messages_in_window - config.messages) * config.per / config.messages)
        if new_slowmode != message.channel.slowmode_delay and new_slowmode > cashed_slowmode_delay:  # type: ignore[union-attr]
            await message.channel.edit(slowmode_delay=new_slowmode, reason=reason_locale)  # type: ignore[union-attr]
    elif message.channel.slowmode_delay != cashed_slowmode_delay:  # type: ignore[union-attr]
        # Reset to cached baseline when below threshold
        await message.channel.edit(slowmode_delay=cashed_slowmode_delay, reason=reset_reason_locale)  # type: ignore[union-attr]
        await _ds_service.restore_slowmode(str(message.channel.id))
