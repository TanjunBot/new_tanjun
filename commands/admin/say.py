import discord

import utility
from localizer import tanjunLocalizer


async def say(commandInfo: utility.commandInfo, channel: discord.TextChannel, *, message: str) -> None:
    if (
        isinstance(commandInfo.user, discord.Member) and isinstance(commandInfo.channel, discord.abc.GuildChannel) and not commandInfo.channel.permissions_for(commandInfo.user).manage_messages
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.missingPermission.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    assert commandInfo.guild is not None
    if not channel.permissions_for(commandInfo.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.missingPermissionBot.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.say.missingPermissionBot.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        await channel.send(message)
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.say.success.description",
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.error.title"),
            description=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.say.error.description"),
        )
        await commandInfo.reply(embed=embed)
