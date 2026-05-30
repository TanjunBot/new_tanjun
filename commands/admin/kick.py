import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo, EmbedColor


async def kick(command_info: utility.CommandInfo, target: discord.Member, reason: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).kick_members
    ):
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale), "commands.admin.kick.missingPermission.description"
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.kick_members:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.kick.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and target.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            colour=EmbedColor.WARNING,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.targetTooHigh.description"),
        )
        await command_info.reply(embed=embed)
        return

    try:
        await target.kick(reason=reason)
        embed = utility.tanjunEmbed(
            colour=EmbedColor.SUCCESS,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.kick.success.description",
                user=target.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.noReasonProvided")
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            colour=EmbedColor.ERROR,
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.kick.error.description"),
        )
        await command_info.reply(embed=embed)
