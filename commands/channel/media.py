import discord

import utility
from api import (
    add_media_channel,
    check_if_opted_out,
    get_media_channel,
    remove_media_channel,
)
from localizer import tanjunLocalizer


async def addMediaChannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        not channel.permissions_for(command_info.guild.me).manage_messages  # type: ignore[union-attr]
        or not channel.permissions_for(command_info.guild.me).read_message_history  # type: ignore[union-attr]
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await get_media_channel(command_info.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.alreadySet.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.alreadySet.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await channel.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.infoMessage.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.infoMessage.description",
            ),
        )
    )

    await add_media_channel(command_info.guild.id, channel.id)  # type: ignore[union-attr]
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.success.title"),
        description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.success.description"),
    )
    await command_info.reply(embed=embed)


async def removeMediaChannel(command_info: utility.CommandInfo, channel: discord.TextChannel) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await get_media_channel(channel.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.notSet.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.notSet.description"),
        )
        await command_info.reply(embed=embed)
        return

    await remove_media_channel(command_info.guild.id, channel.id)  # type: ignore[union-attr]

    await channel.send(
        embed=utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.infoMessageDelete.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.channel.media.infoMessageDelete.description",
            ),
        )
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.channel.media.deleteSuccess.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.admin.channel.media.deleteSuccess.description"
        ),
    )
    await command_info.reply(embed=embed)


async def mediaChannelMessage(message: discord.Message) -> None:
    if not await get_media_channel(message.channel.id):
        return

    if await check_if_opted_out(message.author.id):
        await message.delete()
        await message.author.send(
            embed=utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),  # type: ignore[union-attr]
                    "commands.admin.channel.media.optedOut.title",
                ),
                description=tanjunLocalizer.localize(
                    (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),  # type: ignore[union-attr]
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
                (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),  # type: ignore[union-attr]
                "commands.admin.channel.media.onlyMedia.title",
            ),
            description=tanjunLocalizer.localize(
                (message.guild.preferred_locale if hasattr(message.guild, "preferred_locale") else "en"),  # type: ignore[union-attr]
                "commands.admin.channel.media.onlyMedia.description",
            ),
        )
    )
