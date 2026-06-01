from locale_keys import locale
import discord
import utility

async def deleterole(command_info: utility.CommandInfo, role: discord.Role, reason: str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.deleterole.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    assert command_info.client.user is not None
    bot_member = command_info.guild.get_member(command_info.client.user.id)
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.deleterole.missingPermissionBot.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and command_info.user.top_role.position <= role.position:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.roleTooHigh.title(str(command_info.locale)), description=locale.commands.admin.deleterole.roleTooHigh.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if bot_member and bot_member.top_role.position <= role.position:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.roleTooHighBot.title(str(command_info.locale)), description=locale.commands.admin.deleterole.roleTooHighBot.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    role_name: str = str(role.name)
    try:
        await role.delete(reason=reason)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.forbidden.title(str(command_info.locale)), description=locale.commands.admin.deleterole.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    except discord.HTTPException as e:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.http_error.title(str(command_info.locale)), description=locale.commands.admin.deleterole.http_error.description(str(command_info.locale), status=e.status))
        await command_info.reply(embed=embed)
        return
    except discord.NotFound:
        embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.notfound.title(str(command_info.locale)), description=locale.commands.admin.deleterole.notfound.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    embed = utility.tanjunEmbed(title=locale.commands.admin.deleterole.success.title(str(command_info.locale)), description=locale.commands.admin.deleterole.success.description(str(command_info.locale), role=role_name, reason=reason if reason else 'None'))
    await command_info.reply(embed=embed)
    return