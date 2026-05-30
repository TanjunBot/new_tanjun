from typing import cast

import discord

import utility
from api import clear_channel_overwrites, save_channel_overwrites
from localizer import tanjunLocalizer
from utility import CommandInfo
from utils.checks import check_bot_permission, check_user_permission, send_check_failure


async def lock_channel(command_info: utility.CommandInfo, channel: discord.TextChannel | None = None) -> None:
    if channel is None:
        if command_info.channel is None:
            raise ValueError("Channel is missing in command_info")
        channel = cast(discord.TextChannel, command_info.channel)  # type: ignore[name-defined]

    # User permission check (channel-scoped)
    result = check_user_permission(command_info, "manage_channels", use_guild_permissions=False)
    if await send_check_failure(command_info, "lock", result):
        return

    # Bot permission check (channel-scoped)
    result = check_bot_permission(command_info, "manage_channels", channel=channel)
    if await send_check_failure(command_info, "lock", result):
        return

    try:
        # Clear any existing saved overwrites for this channel
        await clear_channel_overwrites(channel.id)

        # Save current overwrites and update them
        for target, overwrites in channel.overwrites.items():
            if isinstance(target, discord.Role):
                # Using type-safe access to internal attributes for Zenith level
                raw_values = cast(dict[str, bool | None], getattr(overwrites, "_values", {}))  # type: ignore[name-defined]
                overwrite_dict: dict[str, bool] = {k: v for k, v in raw_values.items() if v is not None}
                await save_channel_overwrites(channel.id, target.id, overwrite_dict)  # type: ignore[arg-type]

                # Remove send_messages permission
                overwrites.send_messages = False
                await channel.set_permissions(target, overwrite=overwrites)

        # Update default role permissions
        default_permissions = channel.overwrites_for(channel.guild.default_role)
        default_permissions.send_messages = False
        await channel.set_permissions(channel.guild.default_role, overwrite=default_permissions)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.lock.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.lock.success.description",
                channel=channel.mention,
            ),
        )
        await command_info.reply(embed=embed)

        # Send a message to the locked channel
        locked_message = tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.admin.lock.channelLockedMessage",
            channel=channel.mention,
        )
        await channel.send(locked_message)

    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.lock.forbidden.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.lock.forbidden.description"),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.lock.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.lock.error.description"),
        )
        await command_info.reply(embed=embed)
