import utility
from api import delete_giveaway, get_giveaway
from commands.giveaway.utility import endGiveaway
from localizer import tanjunLocalizer


async def end_giveaway(
    command_info: utility.CommandInfo,
    giveaway_id: int,
) -> None:
    if not command_info.permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    giveaway = await get_giveaway(giveaway_id)
    if not giveaway:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if giveaway.guild_id != str(command_info.guild.id):  # type: ignore[union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if giveaway.ended:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.alreadyEnded.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.error.alreadyEnded.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if not giveaway.started:
        await delete_giveaway(giveaway_id)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.deleted.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.giveaway.end_giveaway_command.deleted.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    await endGiveaway(giveaway_id, command_info.client)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.end_giveaway_command.success.title",
        ),
        description=tanjunLocalizer.localize(
            command_info.locale,
            "commands.giveaway.end_giveaway_command.success.description",
        ),
    )

    await command_info.reply(embed=embed)
