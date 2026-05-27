import contextlib

import discord

from api import addAutoPublish, checkIfChannelIsAutopublish, removeAutoPublish
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def autopublish(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.channel is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not command_info.channel.permissions_for(command_info.user).manage_guild:  # type: ignore[arg-type]
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if await checkIfChannelIsAutopublish(channel.id):
        await removeAutoPublish(channel.id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.is_already.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.is_already.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not channel.is_news():
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.not_news_channel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.not_news_channel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await addAutoPublish(channel.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.autopublish.success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.autopublish.success.description",
        ),
    )
    await command_info.reply(embed=embed)


async def autopublish_remove(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.channel is None:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not command_info.channel.permissions_for(command_info.user).manage_guild:  # type: ignore[arg-type]
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not await checkIfChannelIsAutopublish(channel.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.autopublish.error.is_not.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.autopublish.error.is_not.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await removeAutoPublish(channel.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.autopublish.remove_success.title"),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.utility.autopublish.remove_success.description",
        ),
    )
    await command_info.reply(embed=embed)


async def publish_message(message: discord.Message) -> None:
    if hasattr(message.channel, "is_news") and message.channel.is_news():  # type: ignore[attr-defined, unused-ignore]
        if await checkIfChannelIsAutopublish(message.channel.id):
            with contextlib.suppress(Exception):
                await message.publish()
