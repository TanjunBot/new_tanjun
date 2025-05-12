import aiohttp
import discord

import utility
from localizer import tanjunLocalizer


async def create_emoji(
    commandInfo: utility.commandInfo,
    name: str,
    image_url: str,
    roles: list[discord.Role] = None,
):
    if (
        isinstance(commandInfo.user, discord.Member)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_emojis
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.missingPermission.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createEmoji.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as resp:
                if resp.status != 200:
                    await commandInfo.reply(
                        tanjunLocalizer.localize(
                            commandInfo.locale,
                            "commands.admin.createEmoji.imageDownloadError",
                        )
                    )
                    return
                image_data = await resp.read()

        emoji = await commandInfo.guild.create_custom_emoji(name=name, image=image_data, roles=roles)

        roles_mention = (
            ", ".join([role.mention for role in roles])
            if roles
            else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.allRoles")
        )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.success.title"),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.admin.createEmoji.success.description",
                emoji=str(emoji),
                name=name,
                roles=roles_mention,
            ),
        )
        await commandInfo.reply(embed=embed)

    except discord.HTTPException as e:
        await commandInfo.reply(tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.error", error=str(e)))
