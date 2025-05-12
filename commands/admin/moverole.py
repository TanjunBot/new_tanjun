import discord

import utility
from localizer import tanjunLocalizer


async def moverole(
    commandInfo: utility.commandInfo,
    role: discord.Role,
    target_role: discord.Role,
    position: str,
):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.moverole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.moverole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if role.position >= commandInfo.user.top_role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.roleTooHigh.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.roleTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        if position == "above":
            await role.edit(position=target_role.position)
        else:  # below
            await role.edit(position=target_role.position - 1)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.moverole.success.description",
                role=role.mention,
                target_role=target_role.mention,
                position=position,
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.moverole.error.description"),
        )
        await commandInfo.reply(embed=embed)
