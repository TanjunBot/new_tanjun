import discord

import utility
from localizer import tanjunLocalizer
from services.booster_service import BoosterType, booster_service


async def create_booster_role(command_info: utility.CommandInfo, role: discord.Role) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_roles
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.boosterRole.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")

    if command_info.guild.me.guild_permissions.manage_roles is False:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.boosterRole.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.boosterRole.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    if role is None:
        await booster_service.delete(BoosterType.ROLE, str(command_info.guild.id))
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.roleRemoved.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.boosterRole.roleRemoved.description"
            ),
        )
        await command_info.reply(embed=embed)

        return

    if isinstance(command_info.user, discord.Member) and role.position >= command_info.user.top_role.position:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.targetTooHigh.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.boosterRole.targetTooHigh.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    if command_info.client.user is None:
        raise ValueError("Client user is missing")

    if role.position >= command_info.guild.me.top_role.position:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.roleTooHighBot.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.boosterRole.roleTooHighBot.description",
            ),
        )
        await command_info.reply(embed=embed)

        return

    try:
        await booster_service.add(BoosterType.ROLE, str(command_info.guild.id), str(role.id))
        if role.permissions.administrator:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale),
                    "commands.admin.boosterRole.success.descriptionWarning",
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.success.title"),
                description=tanjunLocalizer.localize(
                    str(command_info.locale), "commands.admin.boosterRole.success.description"
                ),
            )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.boosterRole.error.description"),
        )
        await command_info.reply(embed=embed)
