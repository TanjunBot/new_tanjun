import discord
import utility
from localizer import tanjunLocalizer


async def unban(commandInfo: utility.commandInfo, username: str, reason: str = None):
    if not commandInfo.user.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if not commandInfo.guild.me.guild_permissions.ban_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.missingPermissionBot.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.unban.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        # Get the list of banned users
        bans = [ban_entry async for ban_entry in commandInfo.guild.bans()]

        # Find the user to unban
        user_to_unban = discord.utils.get(bans, user__name=username)

        if user_to_unban is None:
            embed = utility.tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale, "commands.admin.unban.userNotFound.title"
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.admin.unban.userNotFound.description",
                    username=username,
                ),
            )
            await commandInfo.reply(embed=embed)
            return

        await commandInfo.guild.unban(user_to_unban.user, reason=reason)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.success.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.unban.success.description",
                user=user_to_unban.user.name,
                reason=(
                    reason
                    if reason
                    else tanjunLocalizer.localize(
                        commandInfo.locale, "commands.admin.unban.noReasonProvided"
                    )
                ),
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.Forbidden:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.forbidden.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.forbidden.description"
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.error.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.unban.error.description"
            ),
        )
        await commandInfo.reply(embed=embed)
