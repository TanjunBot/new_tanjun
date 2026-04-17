from typing import cast

import discord

import utility
from api import clear_channel_overwrites, save_channel_overwrites
from localizer import tanjunLocalizer


async def lock_channel(commandInfo: utility.CommandInfo, channel: discord.TextChannel | None = None) -> None:
    if channel is None:
        if commandInfo.channel is None:
            raise ValueError("Channel is missing in commandInfo")
        channel = cast(discord.TextChannel, commandInfo.channel)  # type: ignore[name-defined]

    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_channels
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")

    if channel.permissions_for(commandInfo.guild.me).manage_channels is False:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.lock.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)

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
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.success.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.lock.success.description",
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)

        # Send a message to the locked channel
        locked_message = tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.admin.lock.channelLockedMessage",
            channel=channel.mention,
        )
        await channel.send(locked_message)

    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.forbidden.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.lock.error.description"),
        )
        await commandInfo.reply(embed=embed)
