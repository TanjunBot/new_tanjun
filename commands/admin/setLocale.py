import utility
from localizer import tanjunLocalizer


async def set_locale(commandInfo: utility.commandInfo, locale: str):
    if not commandInfo.user.guild_permissions.manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.setLocale.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.setLocale.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await commandInfo.guild.edit(
        preferred_locale=locale,
        reason=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.setLocale.setLocaleReason"),
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.setLocale.success.title"),
        description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.setLocale.success.description"),
    )
    await commandInfo.reply(embed=embed)
    return
