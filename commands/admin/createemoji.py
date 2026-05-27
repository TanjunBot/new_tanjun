import aiohttp
import discord
from aiohttp import ClientTimeout

import utility
from localizer import tanjunLocalizer


async def create_emoji(
    command_info: utility.CommandInfo,
    name: str,
    image_url: str,
    roles: list[discord.Role] | None = None,
) -> None:
    if (
        isinstance(command_info.user, discord.Member)
        and isinstance(command_info.channel, discord.abc.GuildChannel)
        and not command_info.channel.permissions_for(command_info.user).manage_emojis
    ):
        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.createEmoji.missingPermission.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.createEmoji.missingPermission.description",
            ),
        )
        await command_info.reply(embed=embed)
        return

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(image_url, timeout=ClientTimeout(total=10)) as resp,
        ):
            if resp.status != 200:
                await command_info.reply(
                    tanjunLocalizer.localize(
                        str(command_info.locale),
                        "commands.admin.createEmoji.imageDownloadError",
                    )
                )
                return
            image_data = await resp.read()

        assert command_info.guild is not None
        emoji = await command_info.guild.create_custom_emoji(
            name=name, image=image_data, roles=roles if roles is not None else []
        )

        roles_mention = (
            ", ".join([role.mention for role in roles])
            if roles is not None and len(roles) > 0
            else tanjunLocalizer.localize(str(command_info.locale), "commands.admin.createEmoji.allRoles")
        )

        embed = utility.tanjunEmbed(
            title=tanjunLocalizer.localize(str(command_info.locale), "commands.admin.createEmoji.success.title"),
            description=tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.createEmoji.success.description",
                emoji=str(emoji),
                name=name,
                roles=roles_mention,
            ),
        )
        await command_info.reply(embed=embed)

    except (TimeoutError, aiohttp.ClientError):
        await command_info.reply(
            tanjunLocalizer.localize(
                str(command_info.locale),
                "commands.admin.createEmoji.imageDownloadError",
            )
        )
    except discord.HTTPException as e:
        await command_info.reply(
            tanjunLocalizer.localize(str(command_info.locale), "commands.admin.createEmoji.error", error=str(e))
        )
