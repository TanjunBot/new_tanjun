from locale_keys import locale
import discord
import utility

async def remove_timeout(command_info: utility.CommandInfo, member: discord.Member, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).moderate_members):
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.missingPermission.title(command_info.locale), description=locale.commands.admin.remove_timeout.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.missingPermissionBot.title(command_info.locale), description=locale.commands.admin.remove_timeout.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and member.top_role >= command_info.user.top_role:
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.targetTooHigh.title(str(command_info.locale)), description=locale.commands.admin.remove_timeout.targetTooHigh.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    try:
        if not member.is_timed_out():
            embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.notTimedOut.title(command_info.locale), description=locale.commands.admin.remove_timeout.notTimedOut.description(command_info.locale, user=member.name))
            await command_info.reply(embed=embed)
            return
        await member.timeout(None, reason=reason)
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.success.title(str(command_info.locale)), description=locale.commands.admin.remove_timeout.success.description(command_info.locale, user=member.name, reason=reason if reason else locale.commands.admin.remove_timeout.noReasonProvided(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.forbidden.title(str(command_info.locale)), description=locale.commands.admin.remove_timeout.forbidden.description(command_info.locale))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.remove_timeout.error.title(str(command_info.locale)), description=locale.commands.admin.remove_timeout.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)