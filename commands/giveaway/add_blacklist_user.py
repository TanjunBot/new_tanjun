from api import add_giveaway_blacklisted_user as add_blacklist_user_api, check_if_user_blacklisted
import discord
import utility
from localizer import tanjunLocalizer

async def add_blacklist_user(
    commandInfo: utility.commandInfo,
    user: discord.User,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return


    if await check_if_user_blacklisted(commandInfo.guild.id, user.id):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.add_blacklist_user.alreadyBlacklisted.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await add_blacklist_user_api(
        guild_id=commandInfo.guild.id,
        user_id=user.id,
    )

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.add_blacklist_user.success.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.add_blacklist_user.success.description",
        ),
    )
    
    await commandInfo.reply(embed=embed)