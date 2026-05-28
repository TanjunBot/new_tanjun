from typing import cast

import discord

import utility
from api import clear_channel_overwrites, get_channel_overwrites
from localizer import tanjunLocalizer


async def unlock_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None = None) -> None:
    if channel is None:
        assert command_info.channel is not None
        channel = cast(discord.TextChannel, command_info.channel)  # type: ignore[name-defined]

    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.missingPermission.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.unlock.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.unlock.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        # Retrieve saved overwrites
        saved_overwrites = [o async for o in get_channel_overwrites(channel.id)]

        if not saved_overwrites:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.notLocked.title"),
                description=tanjunLocalizer.localize(
                    command_info.locale,
                    "commands.admin.unlock.notLocked.description",
                    channel=channel.mention,
                ),
            )
            await command_info.reply(embed=embed)
            return

        # Restore overwrites
        for overwrite in saved_overwrites:
            role = channel.guild.get_role(int(overwrite.role_id))
            if role:
                await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(**overwrite.overwrites))

        # Clear saved overwrites
        await clear_channel_overwrites(channel.id)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.unlock.success.description",
                channel=channel.mention,
            ),
        )
        await command_info.reply(embed=embed)

        # Send a message to the unlocked channel
        unlocked_message = tanjunLocalizer.localize(
            command_info.locale,
            "commands.admin.unlock.channelUnlockedMessage",
            channel=channel.mention,
        )
        await channel.send(unlocked_message)

    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.unlock.error.description"),
        )
        await command_info.reply(embed=embed)
