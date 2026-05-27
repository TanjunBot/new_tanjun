import discord

from api import set_text_cooldown, set_voice_cooldown
from localizer import tanjunLocalizer
from utility import CommandInfo, tanjunEmbed


async def set_text_cooldown_command(command_info: CommandInfo, cooldown: int) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.settextcooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.settextcooldown.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.settextcooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.settextcooldown.error.invalid_cooldown.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")
    await set_text_cooldown(str(command_info.guild.id), int(cooldown))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.settextcooldown.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.settextcooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await command_info.reply(embed=embed)


async def set_voice_cooldown_command(command_info: CommandInfo, cooldown: int) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).administrator
    ):
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setvoicecooldown.error.no_permission.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setvoicecooldown.error.no_permission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if cooldown < 0:
        embed = tanjunEmbed(
            title=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setvoicecooldown.error.invalid_cooldown.title",
            ),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.level.setvoicecooldown.error.invalid_cooldown.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    if command_info.guild is None:
        raise ValueError("Guild is missing in command_info")
    await set_voice_cooldown(str(command_info.guild.id), int(cooldown))

    embed = tanjunEmbed(
        title=tanjunLocalizer.localize(str(command_info.locale), "commands.level.setvoicecooldown.success.title"),
        description=tanjunLocalizer.localize(
            str(command_info.locale),
            "commands.level.setvoicecooldown.success.description",
            cooldown=cooldown,
        ),
    )
    await command_info.reply(embed=embed)
