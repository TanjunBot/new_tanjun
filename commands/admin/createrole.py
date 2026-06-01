from locale_keys import locale
import discord
import utility

async def createrole(command_info: utility.CommandInfo, name: str, color: discord.Color | str | None=None, reason: str | None=None, hoist: bool=False, mentionable: bool=False, display_icon: discord.Attachment | str | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.createrole.missingPermission.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    assert command_info.guild is not None
    assert command_info.client.user is not None
    bot_member = command_info.guild.get_member(command_info.client.user.id)
    if not bot_member or not bot_member.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.missingPermissionBot.title(command_info.locale), description=locale.commands.admin.createrole.missingPermissionBot.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if not name:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.missingName.title(str(command_info.locale)), description=locale.commands.admin.createrole.missingName.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if len(name) > 100:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.nameTooLong.title(str(command_info.locale)), description=locale.commands.admin.createrole.nameTooLong.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if color and isinstance(color, str):
        if not color.startswith('#'):
            color = '#' + color
        try:
            color = discord.Color(int(color.replace('#', ''), 16))
        except ValueError:
            embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.invalidColor.title(command_info.locale), description=locale.commands.admin.createrole.invalidColor.description(command_info.locale))
            await command_info.reply(embed=embed)
            return
    if reason and len(reason) > 512:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.reasonTooLong.title(str(command_info.locale)), description=locale.commands.admin.createrole.reasonTooLong.description(command_info.locale))
        await command_info.reply(embed=embed)
        return
    if display_icon:
        if 'ROLE_ICONS' not in command_info.guild.features:
            embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.roleIconsNotEnabled.title(command_info.locale), description=locale.commands.admin.createrole.roleIconsNotEnabled.description(command_info.locale))
            await command_info.reply(embed=embed)
            return
        if isinstance(display_icon, discord.Attachment):
            if display_icon.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.invalidIcon.title(command_info.locale), description=locale.commands.admin.createrole.invalidIcon.description(command_info.locale))
                await command_info.reply(embed=embed)
                return
            if display_icon.size > 256000:
                embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.iconTooLarge.title(command_info.locale), description=locale.commands.admin.createrole.iconTooLarge.description(command_info.locale))
                await command_info.reply(embed=embed)
                return
    display_icon_data: bytes | str | None = None
    if isinstance(display_icon, discord.Attachment):
        display_icon_data = await display_icon.read()
    elif isinstance(display_icon, str):
        display_icon_data = display_icon
    try:
        role = await command_info.guild.create_role(name=name, color=color if color is not None else discord.Color.default(), reason=reason, hoist=hoist, mentionable=mentionable, display_icon=display_icon_data)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.forbidden.title(str(command_info.locale)), description=locale.commands.admin.createrole.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    except discord.HTTPException as e:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.http_error.title(str(command_info.locale)), description=locale.commands.admin.createrole.http_error.description(str(command_info.locale), status=e.status))
        await command_info.reply(embed=embed)
        return
    except discord.NotFound:
        embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.notfound.title(str(command_info.locale)), description=locale.commands.admin.createrole.notfound.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    embed = utility.tanjunEmbed(title=locale.commands.admin.createrole.success.title(str(command_info.locale)), description=locale.commands.admin.createrole.success.description(command_info.locale, role=role))
    await command_info.reply(embed=embed)
    return