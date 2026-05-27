import discord

import utility
from localizer import tanjunLocalizer
from utility import CommandInfo


async def remove_timeout(command_info: utility.CommandInfo, member: discord.Member, reason: str | None = None) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).moderate_members
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.missingPermission.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not command_info.guild.me.guild_permissions.moderate_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.missingPermissionBot.title",
            ),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if isinstance(command_info.user, discord.Member) and member.top_role >= CommandInfo.user.top_role:  # type: ignore[misc, union-attr]
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.remove_timeout.targetTooHigh.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.targetTooHigh.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        if not member.is_timed_out():
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.remove_timeout.notTimedOut.title",
                ),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.remove_timeout.notTimedOut.description",
                    user=member.name,
                ),
            )
            await command_info.reply(embed=embed)
            return

        await member.timeout(None, reason=reason)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.remove_timeout.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.success.description",
                user=member.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(
                        command_info.locale,
                        "commands.admin.remove_timeout.noReasonProvided",
                    )
                ),
            ),
        )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.remove_timeout.forbidden.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.remove_timeout.forbidden.description",
            ),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.remove_timeout.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.remove_timeout.error.description"),
        )
        await command_info.reply(embed=embed)
