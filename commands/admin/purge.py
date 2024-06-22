import discord
import utility
from localizer import tanjunLocalizer

async def purge(commandInfo: utility.commandInfo, amount: int, channel: discord.TextChannel = None):
    if channel is None:
        channel = commandInfo.channel

    if not commandInfo.user.guild_permissions.manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.missingPermissionBot.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if amount <= 0:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.invalidAmount.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.invalidAmount.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        deleted = await channel.purge(limit=amount)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.success.description",
                amount=len(deleted),
                channel=channel.mention
            ),
        )
        await channel.send(embed=embed, delete_after=15)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.purge.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.purge.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)