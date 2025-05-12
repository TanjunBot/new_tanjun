import discord

from api import addAutoPublish, checkIfChannelIsAutopublish, removeAutoPublish
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def autopublish(commandInfo: commandInfo, channel: discord.TextChannel):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if await checkIfChannelIsAutopublish(channel.id):
        await removeAutoPublish(channel.id)
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.is_already.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.is_already.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.is_news():
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.not_news_channel.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.not_news_channel.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await addAutoPublish(channel.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.autopublish.success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.autopublish.success.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def autopublish_remove(commandInfo: commandInfo, channel: discord.TextChannel):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not await checkIfChannelIsAutopublish(channel.id):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.autopublish.error.is_not.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.autopublish.error.is_not.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await removeAutoPublish(channel.id)
    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.utility.autopublish.remove_success.title"),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.utility.autopublish.remove_success.description",
        ),
    )
    await commandInfo.reply(embed=embed)


async def publish_message(message: discord.Message):
    if message.channel and hasattr(message.channel, "is_news") and message.channel.is_news():
        if await checkIfChannelIsAutopublish(message.channel.id):
            try:
                await message.publish()
            except Exception:
                pass
