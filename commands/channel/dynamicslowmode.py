import discord
import utility
from localizer import tanjunLocalizer
from api import (
    get_dynamicslowmode_channels,
    add_dynamicslowmode,
    remove_dynamicslowmode,
    get_dynamicslowmode,
    add_dynamicslowmode_message,
    clear_old_dynamicslowmode_messages,
    get_dynamicslowmode_messages,
    cash_slowmode_delay,
    remove_cashed_slowmode_delay,
)
from datetime import datetime, timedelta


async def addDynamicslowmode(
    commandInfo: utility.commandInfo,
    channel: discord.TextChannel,
    messages: int,
    per: int,
    resetafter: int = 60,
):
    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if (
        not channel.permissions_for(commandInfo.guild.me).manage_messages
        or not channel.permissions_for(commandInfo.guild.me).read_message_history
        or not channel.permissions_for(commandInfo.guild.me).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingBotPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingBotPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.alreadySet.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.alreadySet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_dynamicslowmode(
        commandInfo.guild.id, channel.id, messages, per, resetafter
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.channel.dynamicslowmode.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.dynamicslowmode.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def removeDynamicslowmode(
    commandInfo: utility.commandInfo, channel: discord.TextChannel
):
    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await get_dynamicslowmode(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.notSet.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.notSet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_dynamicslowmode(commandInfo.guild.id, channel.id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.dynamicslowmode.deleteSuccess.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.dynamicslowmode.deleteSuccess.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def getDynamicslowmodeChannels(commandInfo: utility.commandInfo):
    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    channels = await get_dynamicslowmode_channels(commandInfo.guild.id)
    if not channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.noChannels.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.dynamicslowmode.noChannels.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    description = ""
    for channel in channels:
        description += tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.channel.dynamicslowmode.channels.description",
            channel_id=channel.channelId,
            messages=channel.messages,
            per=channel.per,
            resetafter=channel.resetafter,
        )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.channel.dynamicslowmode.channels.title"
        ),
        description=description,
    )
    await commandInfo.reply(embed=embed)


async def dynamicslowmodeMessage(message: discord.Message):
    if message.author.bot:
        return

    dynamicSlowmodeChannel = await get_dynamicslowmode(message.channel.id)
    if not dynamicSlowmodeChannel:
        return

    cashed_slowmode_delay = dynamicSlowmodeChannel[5]

    if not cashed_slowmode_delay:
        await cash_slowmode_delay(message.channel.id, message.channel.slowmode_delay)
        cashed_slowmode_delay = message.channel.slowmode_delay

    message_time = message.created_at.replace(tzinfo=None)
    await add_dynamicslowmode_message(
        message.channel.id, message.id, message_time
    )

    dynamicSlowmodeMessages = await get_dynamicslowmode_messages(message.channel.id)

    minTime = message_time - timedelta(seconds=dynamicSlowmodeChannel[4])

    messages = 1
    for dynamicSlowmodeMessage in dynamicSlowmodeMessages:
        if dynamicSlowmodeMessage[3] < minTime:
            messages += 1

    await clear_old_dynamicslowmode_messages(message.channel.id, minTime)

    avgMessages = messages / (
        dynamicSlowmodeChannel[4]
        / (dynamicSlowmodeChannel[3] if dynamicSlowmodeChannel[3] != 0 else 1)
    )
    reasonLocale = tanjunLocalizer.localize(
        (
            message.guild.preferred_locale
            if hasattr(message.guild, "preferred_locale")
            else "en-US"
        ),
        "commands.admin.channel.dynamicslowmode.reason",
        messages=avgMessages,
        per=dynamicSlowmodeChannel[3],
    )
    resetReasonLocale = tanjunLocalizer.localize(
        (
            message.guild.preferred_locale
            if hasattr(message.guild, "preferred_locale")
            else "en-US"
        ),
        "commands.admin.channel.dynamicslowmode.resetReason",
    )
    newSlowmode = int(avgMessages / dynamicSlowmodeChannel[3])
    if (
        newSlowmode != message.channel.slowmode_delay
        and newSlowmode > cashed_slowmode_delay
    ):
        await message.channel.edit(slowmode_delay=newSlowmode, reason=reasonLocale)
    elif (
        newSlowmode < cashed_slowmode_delay
        and message.channel.slowmode_delay != cashed_slowmode_delay
    ):
        await message.channel.edit(
            slowmode_delay=cashed_slowmode_delay, reason=resetReasonLocale
        )
        await remove_cashed_slowmode_delay(message.channel.id)
