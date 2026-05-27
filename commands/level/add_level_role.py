from typing import cast

import discord

from api import add_level_role, get_level_roles
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def add_level_role_command(command_info: CommandInfo, role: discord.Role, level: int) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if level < 1:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.invalid_level.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.invalid_level.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    level_roles = cast(list[tuple[int, int]], await get_level_roles(str(command_info.guild.id)))
    if role.id in [role_id for _, role_id in level_roles]:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.role_exists.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.addlevelrole.error.role_exists.description",
                role=role.mention,
            ),
        )
        await command_info.reply(embed=embed)
        return

    await add_level_role(str(command_info.guild.id), str(role.id), level)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.addlevelrole.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.addlevelrole.success.description",
            role=role.mention,
            level=level,
        ),
    )
    await command_info.reply(embed=embed)
