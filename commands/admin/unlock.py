import discord

import utility
from api import clear_channel_overwrites, get_channel_overwrites
from localizer import tanjunLocalizer


async def unlock_channel(commandInfo: utility.commandInfo, channel: discord.TextChannel = None):
    if channel is None:
        channel = commandInfo.channel

    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.unlock.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.unlock.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        # Retrieve saved overwrites
        saved_overwrites = await get_channel_overwrites(channel.id)

        if not saved_overwrites:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.notLocked.title"),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.unlock.notLocked.description",
                    channel=channel.mention,
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        # Restore overwrites
        for role_id, overwrites in saved_overwrites.items():
            role = channel.guild.get_role(int(role_id))
            if role:
                await channel.set_permissions(role, overwrite=discord.PermissionOverwrite(**overwrites))

        # Clear saved overwrites
        await clear_channel_overwrites(channel.id)

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.unlock.success.description",
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)

        # Send a message to the unlocked channel
        unlocked_message = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.unlock.channelUnlockedMessage",
            channel=channel.mention,
        )
        await channel.send(unlocked_message)

    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.forbidden.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.forbidden.description"),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.error.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.unlock.error.description"),
        )
        await commandInfo.reply(embed=embed)
