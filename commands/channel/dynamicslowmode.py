"""Dynamic slowmode commands — manage per-channel adaptive slowmode."""
import time

import discord

import utility
from locale_keys import locale
from services.dynamicslowmode import DynamicSlowmodeService
_ds_service = DynamicSlowmodeService()

async def addDynamicslowmode(command_info: utility.CommandInfo, channel: discord.TextChannel, messages: int, per: int, resetafter: int=60) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.missingPermission.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.permissions_for(command_info.guild.me).manage_messages or not channel.permissions_for(command_info.guild.me).read_message_history or (not channel.permissions_for(command_info.guild.me).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.missingBotPermission.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.missingBotPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await _ds_service.get_config(str(channel.id)):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.alreadySet.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.alreadySet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await _ds_service.configure(str(command_info.guild.id), str(channel.id), messages, per, resetafter)
    embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.success.title(str(command_info.locale)), description=locale.commands.channel.dynamicslowmode.success.description(command_info.locale))
    await command_info.reply(embed=embed)

async def removeDynamicslowmode(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.missingPermission.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not await _ds_service.get_config(str(channel.id)):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.notSet.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.notSet.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await _ds_service.remove(str(command_info.guild.id), str(channel.id))
    embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.deleteSuccess.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.deleteSuccess.description(command_info.locale))
    await command_info.reply(embed=embed)

async def getDynamicslowmode_channels(command_info: utility.CommandInfo) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_channels):
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.missingPermission.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    channels = await _ds_service.get_all_configs(str(command_info.guild.id))
    if not channels:
        embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.noChannels.title(command_info.locale), description=locale.commands.channel.dynamicslowmode.noChannels.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    description = ''
    for config in channels:
        description += locale.commands.channel.dynamicslowmode.channels.description(command_info.locale, channel_id=config.channel_id, messages=config.messages, per=config.per, resetafter=config.reset_after)
    embed = utility.tanjunEmbed(title=locale.commands.channel.dynamicslowmode.channels.title(str(command_info.locale)), description=description)
    await command_info.reply(embed=embed)

async def dynamicslowmodeMessage(message: discord.Message) -> None:
    """Track messages in-memory and adjust slowmode when thresholds are exceeded."""
    config = await _ds_service.get_config(str(message.channel.id))
    if not config:
        return
    cashed_slowmode_delay = config.cached_slowmode
    if cashed_slowmode_delay is None:
        await _ds_service.cache_current_slowmode(str(message.channel.id), message.channel.slowmode_delay)
        cashed_slowmode_delay = message.channel.slowmode_delay
    now = time.time()
    channel_id: int = message.channel.id
    cutoff = now - config.reset_after
    while _ds_service._recent_messages[channel_id] and _ds_service._recent_messages[channel_id][0] <= cutoff:
        _ds_service._recent_messages[channel_id].popleft()
    _ds_service._recent_messages[channel_id].append(now)
    messages_in_window = len(_ds_service._recent_messages[channel_id])
    reason_locale = locale.commands.channel.dynamicslowmode.reason(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en-US', messages=messages_in_window, per=config.per)
    reset_reason_locale = locale.commands.channel.dynamicslowmode.resetReason(message.guild.preferred_locale if hasattr(message.guild, 'preferred_locale') else 'en-US')
    if messages_in_window > config.messages:
        new_slowmode = int((messages_in_window - config.messages) * config.per / config.messages)
        if new_slowmode != message.channel.slowmode_delay and new_slowmode > cashed_slowmode_delay:
            await message.channel.edit(slowmode_delay=new_slowmode, reason=reason_locale)
    elif message.channel.slowmode_delay != cashed_slowmode_delay:
        await message.channel.edit(slowmode_delay=cashed_slowmode_delay, reason=reset_reason_locale)
        await _ds_service.restore_slowmode(str(message.channel.id))
