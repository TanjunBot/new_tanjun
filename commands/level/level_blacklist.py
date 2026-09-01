from locale_keys import locale
import discord
from api import add_channel_to_blacklist, add_role_to_blacklist, add_user_to_blacklist, get_blacklist, remove_channel_from_blacklist, remove_role_from_blacklist, remove_user_from_blacklist
from utility import CommandInfo, tanjunEmbed

async def add_channel_to_blacklist_command(command_info: CommandInfo, channel: discord.TextChannel, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.add_channel.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.add_channel.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await add_channel_to_blacklist(str(command_info.guild.id), str(channel.id), reason)
    embed = tanjunEmbed(title=locale.commands.level.blacklist.add_channel.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.add_channel.success.description(command_info.locale, channel=channel.mention, reason=reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def remove_channel_from_blacklist_command(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_channel.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.remove_channel.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await remove_channel_from_blacklist(str(command_info.guild.id), str(channel.id))
    embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_channel.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.remove_channel.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)

async def add_role_to_blacklist_command(command_info: CommandInfo, role: discord.Role, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.add_role.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.add_role.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await add_role_to_blacklist(str(command_info.guild.id), str(role.id), reason)
    embed = tanjunEmbed(title=locale.commands.level.blacklist.add_role.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.add_role.success.description(command_info.locale, role=role.mention, reason=reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def remove_role_from_blacklist_command(command_info: CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_role.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.remove_role.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await remove_role_from_blacklist(str(command_info.guild.id), str(role.id))
    embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_role.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.remove_role.success.description(command_info.locale, role=role.mention))
    await command_info.reply(embed=embed)

async def add_user_to_blacklist_command(command_info: CommandInfo, user: discord.Member, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.add_user.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.add_user.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await add_user_to_blacklist(str(command_info.guild.id), str(user.id), reason)
    embed = tanjunEmbed(title=locale.commands.level.blacklist.add_user.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.add_user.success.description(command_info.locale, user=user.mention, reason=reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def remove_user_from_blacklist_command(command_info: CommandInfo, user: discord.Member) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_user.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.remove_user.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    await remove_user_from_blacklist(str(command_info.guild.id), str(user.id))
    embed = tanjunEmbed(title=locale.commands.level.blacklist.remove_user.success.title(str(command_info.locale)), description=locale.commands.level.blacklist.remove_user.success.description(command_info.locale, user=user.mention))
    await command_info.reply(embed=embed)

async def show_blacklist_command(command_info: CommandInfo) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).administrator):
        embed = tanjunEmbed(title=locale.commands.level.blacklist.show.error.no_permission.title(command_info.locale), description=locale.commands.level.blacklist.show.error.no_permission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    blacklist = await get_blacklist(str(command_info.guild.id))
    embed = tanjunEmbed(title=locale.commands.level.blacklist.show.title(str(command_info.locale)), description=locale.commands.level.blacklist.show.description(str(command_info.locale)))
    if blacklist['channels']:
        channel_list = '\n'.join([f'<#{channel_id}> - {(reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale)))}' for channel_id, reason in blacklist['channels']])
        embed.add_field(name=locale.commands.level.blacklist.show.channels(str(command_info.locale)), value=channel_list, inline=False)
    if blacklist['roles']:
        role_list = '\n'.join([f'<@&{role_id}> - {(reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale)))}' for role_id, reason in blacklist['roles']])
        embed.add_field(name=locale.commands.level.blacklist.show.roles(str(command_info.locale)), value=role_list, inline=False)
    if blacklist['users']:
        user_list = '\n'.join([f'<@{user_id}> - {(reason if reason else locale.commands.level.blacklist.no_reason(str(command_info.locale)))}' for user_id, reason in blacklist['users']])
        embed.add_field(name=locale.commands.level.blacklist.show.users(str(command_info.locale)), value=user_list, inline=False)
    if not (blacklist['channels'] or blacklist['roles'] or blacklist['users']):
        embed.description = locale.commands.level.blacklist.show.empty(str(command_info.locale))
    await command_info.reply(embed=embed)