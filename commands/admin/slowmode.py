import discord
import utility
from localizer import tanjunLocalizer

async def set_slowmode(commandInfo: utility.commandInfo, seconds: int, channel: discord.TextChannel = None):
    if channel is None:
        channel = commandInfo.channel

    if not commandInfo.user.guild_permissions.manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.slowmode.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.slowmode.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).manage_channels:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.slowmode.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.slowmode.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if seconds < 0 or seconds > 21600:  # 21600 seconds = 6 hours (Discord's maximum)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.slowmode.invalidDuration.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.slowmode.invalidDuration.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        await channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.slowmode.disabled.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.slowmode.disabled.description",
                    channel=channel.mention
                ),
            )
        else:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.slowmode.enabled.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.slowmode.enabled.description",
                    channel=channel.mention,
                    seconds=seconds
                ),
            )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.slowmode.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.slowmode.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.slowmode.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.slowmode.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)