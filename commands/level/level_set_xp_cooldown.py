import discord

from api import set_text_cooldown, set_voice_cooldown
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def set_text_cooldown_command(CommandInfo: CommandInfo, cooldown: int) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.settextcooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.settextcooldown.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.settextcooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.settextcooldown.error.invalid_cooldown.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")
    await set_text_cooldown(str(commandInfo.guild.id), int(cooldown))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.settextcooldown.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.settextcooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await commandInfo.reply(embed=embed)


async def set_voice_cooldown_command(commandInfo: CommandInfo, cooldown: int) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setvoicecooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setvoicecooldown.error.no_permission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setvoicecooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.level.setvoicecooldown.error.invalid_cooldown.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    if commandInfo.guild is None:
        raise ValueError("Guild is missing in commandInfo")
    await set_voice_cooldown(str(commandInfo.guild.id), int(cooldown))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.level.setvoicecooldown.success.title"),
        description=tanjunLocalizer.localize(
            str(commandInfo.locale),
            "commands.level.setvoicecooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await commandInfo.reply(embed=embed)
