import discord

import utility
from api import add_booster_role, delete_booster_role
from localizer import tanjunLocalizer


async def create_booster_role(commandInfo: utility.commandInfo, role: discord.Role):
    if not commandInfo.user.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.boosterRole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.boosterRole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.boosterRole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not role:
        await delete_booster_role(commandInfo.guild.id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.roleRemoved.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.roleRemoved.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if role.position >= commandInfo.user.top_role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.targetTooHigh.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.boosterRole.targetTooHigh.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if role.position >= commandInfo.client.user.top_role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.roleTooHighBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.boosterRole.roleTooHighBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        await add_booster_role(commandInfo.guild.id, role.id)
        if role.permissions.administrator:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.boosterRole.success.descriptionWarning",
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.success.description"),
            )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.forbidden.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.error.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.boosterRole.error.description"),
        )
        await commandInfo.reply(embed=embed)
