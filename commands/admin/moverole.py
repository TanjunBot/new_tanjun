from locale_keys import locale
import discord
import utility

async def moverole(command_info: utility.CommandInfo, role: discord.Role, target_role: discord.Role, position: str) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.moverole.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.moverole.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and role.position >= command_info.user.top_role.position:
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.roleTooHigh.title(str(command_info.locale)), description=locale.commands.admin.moverole.roleTooHigh.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    try:
        if position == 'above':
            await role.edit(position=target_role.position)
        else:
            await role.edit(position=target_role.position - 1)
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.success.title(str(command_info.locale)), description=locale.commands.admin.moverole.success.description(command_info.locale, role=role.mention, target_role=target_role.mention, position=position))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.forbidden.title(str(command_info.locale)), description=locale.commands.admin.moverole.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.moverole.error.title(str(command_info.locale)), description=locale.commands.admin.moverole.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)