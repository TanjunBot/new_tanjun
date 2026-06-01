from locale_keys import locale
from datetime import UTC, datetime, timedelta
import discord
import utility
from api import add_warning, get_warn_config, get_warnings

async def warn_user(command_info: utility.CommandInfo, member: discord.Member, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).kick_members):
        embed = utility.tanjunEmbed(title=locale.commands.admin.warn.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.warn.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and member.top_role >= command_info.user.top_role:
        embed = utility.tanjunEmbed(title=locale.commands.admin.warn.targetTooHigh.title(str(command_info.locale)), description=locale.commands.admin.warn.targetTooHigh.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    guild_id = command_info.guild.id
    user_id = member.id
    warn_config = await get_warn_config(guild_id)
    expire_date = datetime.now(UTC) + timedelta(days=warn_config.expiration_days)
    await add_warning(guild_id, user_id, reason, expire_date, command_info.user.id)
    warn_count = 0
    async for _ in get_warnings(guild_id, user_id):
        warn_count += 1
    embed = utility.tanjunEmbed(title=locale.commands.admin.warn.success.title(str(command_info.locale)), description=locale.commands.admin.warn.success.description(command_info.locale, user=member.name, reason=reason if reason else locale.commands.admin.warn.noReasonProvided(str(command_info.locale)), count=warn_count))
    await command_info.reply(embed=embed)
    locale_str = str(command_info.locale)
    if warn_config:
        if warn_count >= warn_config.ban_threshold:
            await member.ban(reason=locale.commands.admin.warn.reason.reached_warnings(locale_str, count=warn_count))
        elif warn_count >= warn_config.kick_threshold:
            await member.kick(reason=locale.commands.admin.warn.reason.reached_warnings(locale_str, count=warn_count))
        elif warn_count >= warn_config.timeout_threshold:
            timeout_duration = warn_config.timeout_duration
            duration = timedelta(minutes=timeout_duration)
            until = discord.utils.utcnow() + duration
            await member.timeout(until, reason=locale.commands.admin.warn.reason.reached_warnings(locale_str, count=warn_count))
    try:
        dm_embed = utility.tanjunEmbed(title=locale.commands.admin.warn.dmNotification.title(str(command_info.locale)), description=locale.commands.admin.warn.dmNotification.description(command_info.locale, guild=command_info.guild.name, reason=reason if reason else locale.commands.admin.warn.noReasonProvided(str(command_info.locale)), count=warn_count))
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass