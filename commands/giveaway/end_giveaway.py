import utility
import discord
from localizer import tanjunLocalizer
from api import get_giveaway, delete_giveaway
from giveaway.utility import endGiveaway

async def end_giveaway(
        commandInfo: utility.commandInfo,
        giveawayId: int,
):
    if not commandInfo.permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    giveaway = await get_giveaway(giveawayId)
    if not giveaway:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if giveaway[1] != str(commandInfo.guild.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.notFound.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.notFound.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if giveaway[13]:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.alreadyEnded.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.error.alreadyEnded.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    
    if not giveaway[12]:
        await delete_giveaway(giveawayId)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.deleted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.end_giveaway.deleted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return
    

    await endGiveaway(giveawayId)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.end_giveaway.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.end_giveaway.success.description",
        ),
    )

    await commandInfo.reply(embed=embed)
