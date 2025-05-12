import utility
from localizer import tanjunLocalizer


async def set_locale(commandInfo: utility.commandInfo, locale: str):
    if isinstance(commandInfo.user, discord.Member) and not commandInfo.channel.permissions_for(commandInfo.user).manage_guild:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    await commandInfo.guild.edit(
        preferred_locale=locale,
        reason=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.setLocaleReason"),
    )
    embed = utility.tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.success.title"),
        description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.setLocale.success.description"),
    )
    await commandInfo.reply(embed=embed)
    return
