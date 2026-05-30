import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def moverole(
    command_info: utility.CommandInfo,
    role: discord.Role,
    target_role: discord.Role,
    position: str,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.moverole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.manage_roles:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.moverole.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and role.position >= command_info.user.top_role.position:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.roleTooHigh.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.roleTooHigh.description"),
        )
        await command_info.reply(embed=embed)
        return

    try:
        if position == "above":
            await role.edit(position=target_role.position)
        else:  # below
            await role.edit(position=target_role.position - 1)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.moverole.success.description",
                role=role.mention,
                target_role=target_role.mention,
                position=position,
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.moverole.error.description"),
        )
        await command_info.reply(embed=embed)
