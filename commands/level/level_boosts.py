from locale_keys import locale
import discord
from api import add_channel_boost, add_role_boost, add_user_boost, get_all_boosts, get_channel_boost, get_user_boost, get_user_roles_boosts, remove_channel_boost, remove_role_boost, remove_user_boost
from utility import CommandInfo, tanjunEmbed

async def _require_guild(command_info: CommandInfo) -> bool:
    if command_info.guild is not None:
        return True
    embed = tanjunEmbed(
        title=locale.errors.guildOnly.title(str(command_info.locale)),
        description=locale.errors.guildOnly.description(str(command_info.locale)),
    )
    await command_info.reply(embed=embed)
    return False

async def calculate_user_channel_boost_command(command_info: CommandInfo, user: discord.Member, channel: discord.TextChannel) -> None:
    if not await _require_guild(command_info):
        return
    user_boost = await get_user_boost(str(command_info.guild.id), str(user.id))
    role_boosts = await get_user_roles_boosts(str(command_info.guild.id), [str(role.id) for role in user.roles])
    channel_boost = await get_channel_boost(str(command_info.guild.id), str(channel.id))
    total_additive_boost = 0.0
    total_multiplicative_boost = 1.0
    if user_boost:
        boost_value, is_additive = user_boost
        if is_additive:
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value
    for role_boost in role_boosts:
        boost_value, is_additive = role_boost
        if is_additive:
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value
    if channel_boost:
        boost_value, is_additive = channel_boost
        if is_additive:
            total_additive_boost += boost_value - 1
        else:
            total_multiplicative_boost *= boost_value
    total_boost = (1.0 + total_additive_boost) * total_multiplicative_boost
    embed = tanjunEmbed(title=locale.commands.level.boosts.calculate_user_channel.title(str(command_info.locale)), description=locale.commands.level.boosts.calculate_user_channel.description(command_info.locale, user=user.mention, channel=channel.mention, boost=f'{total_boost:.2f}'))
    await command_info.reply(embed=embed)

async def add_role_boost_command(command_info: CommandInfo, role: discord.Role, boost: float, additive: bool) -> None:
    if not await _require_guild(command_info):
        return
    await add_role_boost(str(command_info.guild.id), str(role.id), boost, additive)
    embed = tanjunEmbed(title=locale.commands.level.boosts.add_role.success.title(str(command_info.locale)), description=locale.commands.level.boosts.add_role.success.description(command_info.locale, role=role.mention, boost=boost, type=locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def add_channel_boost_command(command_info: CommandInfo, channel: discord.TextChannel, boost: float, additive: bool) -> None:
    if not await _require_guild(command_info):
        return
    await add_channel_boost(str(command_info.guild.id), str(channel.id), boost, additive)
    embed = tanjunEmbed(title=locale.commands.level.boosts.add_channel.success.title(str(command_info.locale)), description=locale.commands.level.boosts.add_channel.success.description(command_info.locale, channel=channel.mention, boost=boost, type=locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def add_user_boost_command(command_info: CommandInfo, user: discord.Member, boost: float, additive: bool) -> None:
    if not await _require_guild(command_info):
        return
    await add_user_boost(str(command_info.guild.id), str(user.id), boost, additive)
    embed = tanjunEmbed(title=locale.commands.level.boosts.add_user.success.title(str(command_info.locale)), description=locale.commands.level.boosts.add_user.success.description(command_info.locale, user=user.mention, boost=boost, type=locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale))))
    await command_info.reply(embed=embed)

async def remove_role_boost_command(command_info: CommandInfo, role: discord.Role) -> None:
    if not await _require_guild(command_info):
        return
    await remove_role_boost(str(command_info.guild.id), str(role.id))
    embed = tanjunEmbed(title=locale.commands.level.boosts.remove_role.success.title(str(command_info.locale)), description=locale.commands.level.boosts.remove_role.success.description(command_info.locale, role=role.mention))
    await command_info.reply(embed=embed)

async def remove_channel_boost_command(command_info: CommandInfo, channel: discord.TextChannel) -> None:
    if not await _require_guild(command_info):
        return
    await remove_channel_boost(str(command_info.guild.id), str(channel.id))
    embed = tanjunEmbed(title=locale.commands.level.boosts.remove_channel.success.title(str(command_info.locale)), description=locale.commands.level.boosts.remove_channel.success.description(command_info.locale, channel=channel.mention))
    await command_info.reply(embed=embed)

async def remove_user_boost_command(command_info: CommandInfo, user: discord.Member) -> None:
    if not await _require_guild(command_info):
        return
    await remove_user_boost(str(command_info.guild.id), str(user.id))
    embed = tanjunEmbed(title=locale.commands.level.boosts.remove_user.success.title(str(command_info.locale)), description=locale.commands.level.boosts.remove_user.success.description(command_info.locale, user=user.mention))
    await command_info.reply(embed=embed)

async def show_boosts_command(command_info: CommandInfo) -> None:
    if not await _require_guild(command_info):
        return
    boosts = await get_all_boosts(str(command_info.guild.id))
    embed = tanjunEmbed(title=locale.commands.level.boosts.show.title(str(command_info.locale)), description=locale.commands.level.boosts.show.description(str(command_info.locale)))
    if boosts['roles']:
        role_boosts = '\n'.join([f'<@&{role_id}>: {boost} ({(locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale)))})' for role_id, boost, additive in boosts['roles']])
        embed.add_field(name=locale.commands.level.boosts.show.roles(str(command_info.locale)), value=role_boosts, inline=False)
    if boosts['channels']:
        channel_boosts = '\n'.join([f'<#{channel_id}>: {boost} ({(locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale)))})' for channel_id, boost, additive in boosts['channels']])
        embed.add_field(name=locale.commands.level.boosts.show.channels(str(command_info.locale)), value=channel_boosts, inline=False)
    if boosts['users']:
        user_boosts = '\n'.join([f'<@{user_id}>: {boost} ({(locale.commands.level.boosts.additive(str(command_info.locale)) if additive else locale.commands.level.boosts.multiplicative(str(command_info.locale)))})' for user_id, boost, additive in boosts['users']])
        embed.add_field(name=locale.commands.level.boosts.show.users(str(command_info.locale)), value=user_boosts, inline=False)
    if not (boosts['roles'] or boosts['channels'] or boosts['users']):
        embed.description = locale.commands.level.boosts.show.no_boosts(str(command_info.locale))
    await command_info.reply(embed=embed)