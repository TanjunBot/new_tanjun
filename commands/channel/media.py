import discord

import utility
from api import (
    add_media_channel,
    check_if_opted_out,
    get_media_channel,
    remove_media_channel,
)
from localizer import tanjunLocalizer


async def addMediaChannel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if (
        not channel.permissions_for(commandInfo.guild.me).manage_messages
        or not channel.permissions_for(commandInfo.guild.me).read_message_history
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await get_media_channel(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.alreadySet.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.alreadySet.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await channel.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.infoMessage.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.infoMessage.description",
            ),
        )
    )

    await add_media_channel(commandInfo.guild.id, channel.id)
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.success.description"),
    )
    await commandInfo.reply(embed=embed)


async def removeMediaChannel(commandInfo: utility.commandInfo, channel: discord.TextChannel):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await get_media_channel(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.notSet.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.notSet.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_media_channel(commandInfo.guild.id, channel.id)

    await channel.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.infoMessageDelete.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.channel.media.infoMessageDelete.description",
            ),
        )
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.channel.media.deleteSuccess.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale), "commands.admin.channel.media.deleteSuccess.description"
        ),
    )
    await commandInfo.reply(embed=embed)


async def mediaChannelMessage(message: discord.Message):
    if message.author.bot:
        return

    if not await get_media_channel(message.channel.id):
        return

    if await check_if_opted_out(message.author.id):
        await message.delete()
        await message.author.send(
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),
                    "commands.admin.channel.media.optedOut.title",
                ),
                description=tanjunLocalizer.localize(
                    (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),
                    "commands.admin.channel.media.optedOut.description",
                ),
            )
        )
        return

    if len(message.attachments) > 0:
        return

    await message.delete()
    await message.author.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),
                "commands.admin.channel.media.onlyMedia.title",
            ),
            description=tanjunLocalizer.localize(
                (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),
                "commands.admin.channel.media.onlyMedia.description",
            ),
        )
    )
