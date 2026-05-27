import discord

import utility
from localizer import tanjunLocalizer


async def unban(command_info: utility.CommandInfo, username: str, reason: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).ban_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.unban.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.unban.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        # Get the list of banned users
        bans = [ban_entry async for ban_entry in command_info.guild.bans()]

        # Find the user to unban
        user_to_unban = discord.utils.get(bans, user__name=username)

        if user_to_unban is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.userNotFound.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.unban.userNotFound.description",
                    username=username,
                ),
            )
            await command_info.reply(embed=embed)
            return

        await command_info.guild.unban(user_to_unban.user, reason=reason)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.unban.success.description",
                user=user_to_unban.user.name,
                reason=(
                    reason
                    if reason is not None and len(reason.strip()) > 0
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.noReasonProvided")
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unban.error.description"),
        )
        await command_info.reply(embed=embed)
