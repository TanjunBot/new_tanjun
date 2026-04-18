from datetime import timedelta

import discord

import utility
from api import (
    add_dynamicslowmode,
    add_dynamicslowmode_message,
    cash_slowmode_delay,
    clear_old_dynamicslowmode_messages,
    get_dynamicslowmode,
    get_dynamicslowmode_channels,
    get_dynamicslowmode_messages,
    remove_cashed_slowmode_delay,
    remove_dynamicslowmode,
)
from localizer import tanjunLocalizer


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
    if message.author.bot:
        return

    dynamicSlowmodeChannel = await get_dynamicslowmode(message.channel.id)
    if not dynamicSlowmodeChannel:
        return

    cashed_slowmode_delay = dynamicSlowmodeChannel.cached_slowmode

    if not cashed_slowmode_delay:
        await cash_slowmode_delay(message.channel.id, message.channel.slowmode_delay)  # type: ignore[union-attr, arg-type]
        cashed_slowmode_delay = message.channel.slowmode_delay  # type: ignore[union-attr]

    message_time = message.created_at.replace(tzinfo=None)
    await add_dynamicslowmode_message(message.channel.id, message.id, message_time)  # type: ignore[arg-type]

    dynamicSlowmodeMessages = await get_dynamicslowmode_messages(message.channel.id)

    minTime = message_time - timedelta(seconds=dynamicSlowmodeChannel.reset_after)

    messages = 1
    for dynamicSlowmodeMessage in dynamicSlowmodeMessages:  # type: ignore[union-attr]
        if dynamicSlowmodeMessage.send_time < minTime:
            messages += 1

    await clear_old_dynamicslowmode_messages(message.channel.id, minTime)

    reasonLocale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.reason",
        messages=messages,
        per=dynamicSlowmodeChannel.per,
    )
    resetReasonLocale = tanjunLocalizer.localize(
        (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en-US"),  # type: ignore[union-attr]
        "commands.channel.dynamicslowmode.resetReason",
    )
    newSlowmode = int(messages / dynamicSlowmodeChannel.per)
    if newSlowmode != message.channel.slowmode_delay and newSlowmode > cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=newSlowmode, reason=reasonLocale)  # type: ignore[union-attr]
    elif newSlowmode < cashed_slowmode_delay and message.channel.slowmode_delay != cashed_slowmode_delay:  # type: ignore[union-attr]
        await message.channel.edit(slowmode_delay=cashed_slowmode_delay, reason=resetReasonLocale)  # type: ignore[union-attr]
        await remove_cashed_slowmode_delay(message.channel.id)
