from typing import cast

import discord

import utility
from localizer import tanjunLocalizer


async def set_slowmode(command_info: utility.CommandInfo, seconds: int, channel: discord.TextChannel | None = None) -> None:
    if channel is None:
        assert command_info.channel is not None
        channel = cast(discord.TextChannel, command_info.channel)  # type: ignore[name-defined]

    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.slowmode.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.slowmode.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if seconds < 0 or seconds > 21600:  # 21600 seconds = 6 hours (Discord's maximum)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.invalidDuration.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.slowmode.invalidDuration.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        await channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.disabled.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.slowmode.disabled.description",
                    channel=channel.mention,
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.enabled.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.slowmode.enabled.description",
                    channel=channel.mention,
                    seconds=seconds,
                ),
            )
        await command_info.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.slowmode.error.description"),
        )
        await command_info.reply(embed=embed)
