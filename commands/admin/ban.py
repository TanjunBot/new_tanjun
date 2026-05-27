import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def ban(
    command_info: utility.CommandInfo,
    target: discord.Member,
    reason: str | None = None,
    delete_message_days: int = 0,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).ban_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.missingPermission.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.missingPermission.description"),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.ban.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and target.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.targetTooHigh.description"),
        )
        await command_info.reply(embed=embed)
        return

    try:
        await target.ban(reason=reason, delete_message_days=delete_message_days)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.ban.success.description",
                user=target.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.noReasonProvided")
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.ban.error.description"),
        )
        await command_info.reply(embed=embed)
