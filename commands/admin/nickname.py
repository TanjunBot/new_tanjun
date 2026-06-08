from locale_keys import locale
import discord
import utility

async def change_nickname(command_info: utility.CommandInfo, member: discord.Member, nickname: str | None=None) -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(title=locale.errors.guildOnly.title(str(command_info.locale)), description=locale.errors.guildOnly.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_nicknames):
        embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.nickname.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not command_info.guild.me.guild_permissions.manage_nicknames:
        embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.nickname.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and member.top_role >= command_info.user.top_role and (command_info.user != command_info.guild.owner):
        embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.targetTooHigh.title(str(command_info.locale)), description=locale.commands.admin.nickname.targetTooHigh.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    try:
        old_nick = member.nick or member.name
        await member.edit(nick=nickname)
        if nickname:
            embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.changed.title(str(command_info.locale)), description=locale.commands.admin.nickname.changed.description(command_info.locale, user=member.mention, old_nick=old_nick, new_nick=nickname))
        else:
            embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.removed.title(str(command_info.locale)), description=locale.commands.admin.nickname.removed.description(command_info.locale, user=member.name, old_nick=old_nick))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.forbidden.title(str(command_info.locale)), description=locale.commands.admin.nickname.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.nickname.error.title(str(command_info.locale)), description=locale.commands.admin.nickname.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)