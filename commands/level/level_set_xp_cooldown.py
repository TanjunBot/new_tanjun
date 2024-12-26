from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import set_text_cooldown, set_voice_cooldown


async def set_text_cooldown_command(commandInfo: commandInfo, cooldown: int):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.settextcooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.settextcooldown.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.settextcooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.settextcooldown.error.invalid_cooldown.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_text_cooldown(str(commandInfo.guild.id), cooldown)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.settextcooldown.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.settextcooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await commandInfo.reply(embed=embed)


async def set_voice_cooldown_command(commandInfo: commandInfo, cooldown: int):
    if not commandInfo.user.guild_permissions.administrator:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setvoicecooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setvoicecooldown.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setvoicecooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.level.setvoicecooldown.error.invalid_cooldown.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    await set_voice_cooldown(str(commandInfo.guild.id), cooldown)

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(
            commandInfo.locale, "commands.level.setvoicecooldown.success.title"
        ),
        description=tanjunLocalizer.localize(
            commandInfo.locale,
            "commands.level.setvoicecooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await commandInfo.reply(embed=embed)
