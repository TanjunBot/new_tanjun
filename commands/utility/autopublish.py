from locale_keys import locale
import contextlib
import discord
from api import addAutoPublish, checkIfChannelIsAutopublish, removeAutoPublish
from utility import CommandInfo, tanjunEmbed

async def autopublish(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        embed = tanjunEmbed(title=locale.errors.guildOnly.title(command_info.locale), description=locale.errors.guildOnly.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if command_info.channel is None:
        embed = tanjunEmbed(title=locale.errors.noChannel.title(command_info.locale), description=locale.errors.noChannel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not command_info.channel.permissions_for(command_info.user).manage_guild:
        embed = tanjunEmbed(title=locale.commands.utility.autopublish.error.no_permission.title(command_info.locale), description=locale.commands.utility.autopublish.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if await checkIfChannelIsAutopublish(channel.id):
        await removeAutoPublish(channel.id)
        embed = tanjunEmbed(title=locale.commands.utility.autopublish.error.is_already.title(command_info.locale), description=locale.commands.utility.autopublish.error.is_already.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not channel.is_news():
        embed = tanjunEmbed(title=locale.commands.utility.autopublish.error.not_news_channel.title(command_info.locale), description=locale.commands.utility.autopublish.error.not_news_channel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await addAutoPublish(channel.id)
    embed = tanjunEmbed(title=locale.commands.utility.autopublish.success.title(str(command_info.locale)), description=locale.commands.utility.autopublish.success.description(command_info.locale))
    await command_info.reply(embed=embed)

async def autopublish_remove(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if command_info.guild is None:
        embed = tanjunEmbed(title=locale.errors.guildOnly.title(command_info.locale), description=locale.errors.guildOnly.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if command_info.channel is None:
        embed = tanjunEmbed(title=locale.errors.noChannel.title(command_info.locale), description=locale.errors.noChannel.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not command_info.channel.permissions_for(command_info.user).manage_guild:
        embed = tanjunEmbed(title=locale.commands.utility.autopublish.error.no_permission.title(command_info.locale), description=locale.commands.utility.autopublish.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not await checkIfChannelIsAutopublish(channel.id):
        embed = tanjunEmbed(title=locale.commands.utility.autopublish.error.is_not.title(str(command_info.locale)), description=locale.commands.utility.autopublish.error.is_not.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    await removeAutoPublish(channel.id)
    embed = tanjunEmbed(title=locale.commands.utility.autopublish.remove_success.title(str(command_info.locale)), description=locale.commands.utility.autopublish.remove_success.description(command_info.locale))
    await command_info.reply(embed=embed)

async def publish_message(message: discord.Message) -> None:
    if hasattr(message.channel, 'is_news') and message.channel.is_news():
        if await checkIfChannelIsAutopublish(message.channel.id):
            with contextlib.suppress(discord.Forbidden, discord.HTTPException, discord.NotFound):
                await message.publish()