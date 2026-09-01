from locale_keys import locale
import discord
import utility
from services.booster_service import BoosterType, booster_service

async def create_booster_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_roles):
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if command_info.guild is None:
        raise ValueError('Guild is missing in command_info')
    if command_info.guild.me.guild_permissions.manage_roles is False:
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.missingPermissionBot.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.missingPermissionBot.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if role is None:
        await booster_service.delete(BoosterType.ROLE, str(command_info.guild.id))
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.roleRemoved.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.roleRemoved.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if isinstance(command_info.user, discord.Member) and role.position >= command_info.user.top_role.position:
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.targetTooHigh.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.targetTooHigh.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    if command_info.client.user is None:
        raise ValueError('Client user is missing')
    if role.position >= command_info.guild.me.top_role.position:
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.roleTooHighBot.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.roleTooHighBot.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    try:
        await booster_service.add(BoosterType.ROLE, str(command_info.guild.id), str(role.id))
        if role.permissions.administrator:
            embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.success.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.success.descriptionWarning(str(command_info.locale)))
        else:
            embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.success.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.success.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.forbidden.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.forbidden.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(title=locale.commands.admin.boosterRole.error.title(str(command_info.locale)), description=locale.commands.admin.boosterRole.error.description(str(command_info.locale)))
        await command_info.reply(embed=embed)