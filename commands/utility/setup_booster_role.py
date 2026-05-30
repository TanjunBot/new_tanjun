import discord

import utility
from localizer import tanjunLocalizer
from services.booster_service import BoosterType, booster_service
from utility import CommandInfo, tanjunEmbed


async def setupBoosterRole(command_info: CommandInfo, role: discord.Role) -> None:
    if isinstance(command_info.user, discord.User) or command_info.guild is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildonly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildonly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not getattr(command_info.user, "guild_permissions", None) or not command_info.user.guild_permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterrole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterrole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    booster_role = await booster_service.get(BoosterType.ROLE, str(command_info.guild.id))
    if booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterrole.already_set.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.setupboosterrole.already_set.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await booster_service.add(BoosterType.ROLE, str(command_info.guild.id), str(role.id))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.setupboosterrole.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.utility.setupboosterrole.success.description"
        ),
    )
    await command_info.reply(embed=embed)
