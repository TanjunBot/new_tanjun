from api import get_giveaway_blacklisted_roles as get_blacklist_role_api, get_giveaway_blacklisted_users as get_blacklist_user_api
import discord
import utility
from localizer import tanjunLocalizer

async def list_blacklist(
    commandInfo: utility.commandInfo,
):
    if not commandInfo.permissions.administrator:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.list_blacklist.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.list_blacklist.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    blacklistedRoles = [role[0] for role in await get_blacklist_role_api(commandInfo.guild.id)]
    blacklistedUsers = [user[0] for user in await get_blacklist_user_api(commandInfo.guild.id)]

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.list_blacklist.title",
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.giveaway.list_blacklist.description",
        ),
    )

    if blacklistedRoles:
        embed.add_field(
            name=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.list_blacklist.roles",
            ),
            value="\n".join([f"<@&{role}>" for role in blacklistedRoles]),
            inline=False,
        )

    if blacklistedUsers:
        embed.add_field(
            name=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.giveaway.list_blacklist.users",
            ),
            value="\n".join([f"<@{user}>" for user in blacklistedUsers]),
            inline=False,
        )

    await commandInfo.reply(embed=embed)