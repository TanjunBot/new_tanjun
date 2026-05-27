
import aiohttp
import discord
from aiohttp import ClientTimeout

import utility
from localizer import tanjunLocalizer


async def create_emoji(
    commandInfo: utility.CommandInfo,
    name: str,
    image_url: str,
    roles: list[discord.Role] | None = None,
) -> None:
    if (
        isinstance(commandInfo.user, discord.Member)
        and isinstance(commandInfo.channel, discord.abc.GuildChannel)
        and not commandInfo.channel.permissions_for(commandInfo.user).manage_emojis
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.createEmoji.missingPermission.description",
            ),
        )
        await commandInfo.reply(embed=embed)
        return

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(image_url, timeout=ClientTimeout(total=10)) as resp,
        ):
            if resp.status != 200:
                await commandInfo.reply(
                    tanjunLocalizer.localize(
                        str(commandInfo.locale),
                        "commands.admin.createEmoji.imageDownloadError",
                    )
                )
                return
            image_data = await resp.read()

        assert commandInfo.guild is not None
        emoji = await commandInfo.guild.create_custom_emoji(
            name=name, image=image_data, roles=roles if roles is not None else []
        )

        roles_mention = (
            ", ".join([role.mention for role in roles])
            if roles is not None and len(roles) > 0
            else tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.allRoles")
        )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.success.title"),
            description=tanjunLocalizer.localize(
                str(commandInfo.locale),
                "commands.admin.createEmoji.success.description",
                emoji=str(emoji),
                name=name,
                roles=roles_mention,
            ),
        )
        await commandInfo.reply(embed=embed)

    except (TimeoutError, discord.HTTPException, aiohttp.ClientError) as e:
        await commandInfo.reply(
            tanjunLocalizer.localize(str(commandInfo.locale), "commands.admin.createEmoji.error", error=str(e))
        )
