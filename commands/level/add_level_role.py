
import discord

from api import add_level_role, get_level_roles
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def add_level_role_command(commandInfo: CommandInfo, role: discord.Role, level: int) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if level < 1:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.invalid_level.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.invalid_level.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    level_roles = [lr async for lr in get_level_roles(str(commandInfo.guild.id))]
    if role.id in [int(lr.role_id) for lr in level_roles]:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.role_exists.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.addlevelrole.error.role_exists.description",
                role=role.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_level_role(str(commandInfo.guild.id), str(role.id), level)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.addlevelrole.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.addlevelrole.success.description",
            role=role.mention,
            level=level,
        ),
    )
    await commandInfo.reply(embed=embed)
