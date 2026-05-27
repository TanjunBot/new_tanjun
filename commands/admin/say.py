import discord

import utility
from localizer import tanjunLocalizer


async def say(command_info: utility.CommandInfo, channel: discord.TextChannel, *, message: str) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_messages
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.missingPermission.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.missingPermission.description"),
        )
        await command_info.reply(embed=embed)
        return

    assert command_info.guild is not None
    if not channel.permissions_for(command_info.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.say.missingPermissionBot.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        await channel.send(message)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.success.title"),
            description=tanjunLocalizer.localize(
                command_info.locale,
                "commands.admin.say.success.description",
                channel=channel.mention,
            ),
        )
        await command_info.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.error.title"),
            description=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.say.error.description"),
        )
        await command_info.reply(embed=embed)
