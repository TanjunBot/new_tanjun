import discord

from api import get_level_role, remove_level_role
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def remove_level_role_command(command_info: CommandInfo, role: discord.Role) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.removelevelrole.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.removelevelrole.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    existing_role = await get_level_role(str(command_info.guild.id), str(role.id))
    if not existing_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.removelevelrole.error.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.removelevelrole.error.role_not_found.description",
                role=role.mention,
            ),
        )
        await command_info.reply(embed=embed)
        return

    await remove_level_role(str(command_info.guild.id), str(role.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.removelevelrole.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.removelevelrole.success.description",
            role=role.mention,
        ),
    )
    await command_info.reply(embed=embed)
