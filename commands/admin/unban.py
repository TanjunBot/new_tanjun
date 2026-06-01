from locale_keys import locale
import discord
import utility

async def unban(command_info: utility.CommandInfo, username: str, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).ban_members):
        embed = utility.tanjunEmbed(title=locale.commands.admin.unban.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.unban.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(title=locale.commands.admin.unban.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.unban.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    try:
        bans = [ban_entry async for ban_entry in command_info.guild.bans()]
        user_to_unban = discord.utils.get(bans, user__name=username)
        if user_to_unban is None:
            embed = utility.tanjunEmbed(title=locale.commands.admin.unban.userNotFound.title(str(command_info.locale)), description=locale.commands.admin.unban.userNotFound.description(command_info.locale, username=username))
            await command_info.reply(embed=embed)
            return
        await command_info.guild.unban(user_to_unban.user, reason=reason)
        embed = utility.tanjunEmbed(title=locale.commands.admin.unban.success.title(str(command_info.locale)), description=locale.commands.admin.unban.success.description(command_info.locale, user=user_to_unban.user.name, reason=reason if reason is not None and len(reason.strip()) > 0 else locale.commands.admin.unban.noReasonProvided(str(command_info.locale))))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.unban.forbidden.title(str(command_info.locale)), description=locale.commands.admin.unban.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.unban.error.title(str(command_info.locale)), description=locale.commands.admin.unban.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)