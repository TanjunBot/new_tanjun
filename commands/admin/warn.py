import discord
import utility
from localizer import tanjunLocalizer
from api import add_warning, get_warnings

async def warn_user(commandInfo: utility.commandInfo, member: discord.Member, reason: str = None):
    if not commandInfo.user.guild_permissions.kick_members:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.warn.missingPermission.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warn.missingPermission.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if member.top_role >= commandInfo.user.top_role:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.warn.targetTooHigh.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warn.targetTooHigh.description"
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    guild_id = commandInfo.guild.id
    user_id = member.id

    add_warning(guild_id, user_id, reason)
    warn_count, warn_reasons = get_warnings(guild_id, user_id)

    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.admin.warn.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.admin.warn.success.description",
            user=member.name,
            reason=reason if reason else tanjunLocalizer.localize(commandInfo.locale, "commands.admin.warn.noReasonProvided"),
            count=warn_count
        ),
    )
    await commandInfo.reply(embed=embed)

    # DM the warned user
    try:
        dm_embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale, "commands.admin.warn.dmNotification.title"
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.warn.dmNotification.description",
                guild=commandInfo.guild.name,
                reason=reason if reason else tanjunLocalizer.localize(commandInfo.locale, "commands.admin.warn.noReasonProvided"),
                count=warn_count
            ),
        )
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        # If we can't DM the user, we'll just ignore it
        pass