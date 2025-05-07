import discord

import utility
from localizer import tanjunLocalizer


async def say(commandInfo: utility.commandInfo, channel: discord.TextChannel, *, message: str):
    if not commandInfo.user.guild_permissions.manage_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.missingPermission.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.missingPermission.description"),
        )
        await commandInfo.reply(embed=embed)
        return

    if not channel.permissions_for(commandInfo.guild.me).send_messages:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.missingPermissionBot.title"),
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
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.say.success.description",
                channel=channel.mention,
            ),
        )
        await commandInfo.reply(embed=embed)
    except discord.HTTPException:
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.error.title"),
            description=tanjunLocalizer.localize(commandInfo.locale, "commands.admin.say.error.description"),
        )
        await commandInfo.reply(embed=embed)
