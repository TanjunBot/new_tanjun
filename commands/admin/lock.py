import discord
import utility
from localizer import tanjunLocalizer
from api import save_channel_overwrites, clear_channel_overwrites


async def lock_channel(
    commandInfo: utility.commandInfo, channel: discord.TextChannel = None
):
    if channel is None:
        channel = commandInfo.channel

    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.lock.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        # Clear any existing saved overwrites for this channel
        await clear_channel_overwrites(channel.id)

        # Save current overwrites and update them
        for role, overwrites in channel.overwrites.items():
            if isinstance(role, discord.Role):
                overwrite_dict = {
                    k: v for k, v in overwrites._values.items() if v is not None
                }
                await save_channel_overwrites(channel.id, role.id, overwrite_dict)

                # Remove send_messages permission
                overwrites.send_messages = False
                await channel.set_permissions(role, overwrite=overwrites)

        # Update default role permissions
        default_permissions = channel.overwrites_for(channel.guild.default_role)
        default_permissions.send_messages = False
        await channel.set_permissions(
            channel.guild.default_role, overwrite=default_permissions
        )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.lock.success.description",
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)

        # Send a message to the locked channel
        locked_message = tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.lock.channelLockedMessage",
            channel=channel.mention,
        )
        await channel.send(locked_message)

    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.lock.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)
