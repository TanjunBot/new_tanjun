import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def kick(commandInfo: utility.CommandInfo, target: discord.Member, reason: str | None = None) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).kick_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if not commandInfo.guild.me.guild_permissions.kick_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.kick.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if isinstance(commandInfo.user, discord.Member) and target.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.targetTooHigh.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.targetTooHigh.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        await target.kick(reason=reason)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.kick.success.description",
                user=target.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.noReasonProvided")
                ),
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.kick.error.description"),
        )
        await commandInfo.reply(embed=embed)
