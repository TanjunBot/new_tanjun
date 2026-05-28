import discord

import utility
from api import delete_booster_role, get_booster_role
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def deleteBoosterRole(command_info: CommandInfo) -> None:
    if command_info.guild is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.guildOnly.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.channel is None:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "errors.noChannel.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if (
        isinstance(command_info.user, discord.Member)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterrole.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterrole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    booster_role = await get_booster_role(command_info.guild.id)
    if not booster_role:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterrole.no_booster_role.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.utility.deleteboosterrole.no_booster_role.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await delete_booster_role(command_info.guild.id)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.utility.deleteboosterrole.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale), "commands.utility.deleteboosterrole.success.description"
        ),
    )
    await command_info.reply(embed=embed)
