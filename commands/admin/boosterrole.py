import discord

import utility
from api import add_booster_role, delete_booster_role
from localizer import tanjunLocalizer


async def create_booster_role(commandInfo: utility.CommandInfo, role: discord.Role) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.boosterRole.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)

        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")

    if commandInfo.guild.me.guild_permissions.manage_roles is False:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.boosterRole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.boosterRole.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)

        return

    if role is None:
        await delete_booster_role(int(commandInfo.guild.id))
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.roleRemoved.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale), "commands.admin.boosterRole.roleRemoved.description"
            ),
        )
        await commandInfo.reply(embed=embed)

        return

    if isinstance(commandInfo.user, discord.Member) and role.position >= CommandInfo.user.top_role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.targetTooHigh.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.boosterRole.targetTooHigh.description",
            ),
        )
        await commandInfo.reply(embed=embed)

        return

    if commandInfo.client.user is None:
        raise ValueError("Client user is missing")

    if role.position >= CommandInfo.guild.me.top_role.position:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.roleTooHighBot.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.boosterRole.roleTooHighBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)

        return

    try:
        await add_booster_role(int(commandInfo.guild.id), int(role.id))
        if role.permissions.administrator:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(
                    str(commandInfo.locale),
                    "commands.admin.boosterRole.success.descriptionWarning",
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(
                    str(commandInfo.locale), "commands.admin.boosterRole.success.description"
                ),
            )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.boosterRole.error.description"),
        )
        await commandInfo.reply(embed=embed)
