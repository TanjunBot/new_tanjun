import discord  # type: ignore[import-not-found]

from api import get_level_role, remove_level_role
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def remove_level_role_command(commandInfo: CommandInfo, role: discord.Role) -> None:  # type: ignore[no-any-unimported]
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.removelevelrole.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.removelevelrole.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    existing_role = await get_level_role(str(commandInfo.guild.id), str(role.id))
    if not existing_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.removelevelrole.error.role_not_found.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.removelevelrole.error.role_not_found.description",
                role=role.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await remove_level_role(str(commandInfo.guild.id), str(role.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.removelevelrole.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.removelevelrole.success.description",
            role=role.mention,
        ),
    )
    await commandInfo.reply(embed=embed)
