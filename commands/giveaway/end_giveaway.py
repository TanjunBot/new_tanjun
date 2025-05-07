import utility
from api import delete_giveaway, get_giveaway
from commands.giveaway.utility import endGiveaway
from localizer import tanjunLocalizer


async def end_giveaway(
    commandInfo: utility.commandInfo,
    giveawayId: int,
):
    if not commandInfo.permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    giveaway = await get_giveaway(giveawayId)
    if not giveaway:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if giveaway[1] != str(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if giveaway[13]:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.alreadyEnded.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.error.alreadyEnded.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not giveaway[12]:
        await delete_giveaway(giveawayId)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.deleted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway_command.deleted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await endGiveaway(giveawayId, commandInfo.client)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.end_giveaway_command.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.end_giveaway_command.success.description",
        ),
    )

    await commandInfo.reply(embed=embed)
