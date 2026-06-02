from locale_keys import locale
import aiohttp
import discord
from aiohttp import ClientTimeout
import utility

async def create_emoji(command_info: utility.CommandInfo, name: str, image_url: str, roles: list[discord.Role] | None=None) -> None:
    if isinstance(command_info.user, discord.Member) and isinstance(command_info.channel, discord.abc.GuildChannel) and (not command_info.channel.permissions_for(command_info.user).manage_emojis):
        embed = utility.tanjunEmbed(title=locale.commands.admin.createEmoji.missingPermission.title(str(command_info.locale)), description=locale.commands.admin.createEmoji.missingPermission.description(str(command_info.locale)))
        await command_info.reply(embed=embed)
        return
    try:
        async with aiohttp.ClientSession() as session, session.get(image_url, timeout=ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                await command_info.reply(locale.commands.admin.createEmoji.imageDownloadError(str(command_info.locale)))
                return
            image_data = await resp.read()
        assert command_info.guild is not None
        emoji = await command_info.guild.create_custom_emoji(name=name, image=image_data, roles=roles if roles is not None else [])
        roles_mention = ', '.join([role.mention for role in roles]) if roles is not None and len(roles) > 0 else locale.commands.admin.createEmoji.allRoles(str(command_info.locale))
        embed = utility.tanjunEmbed(title=locale.commands.admin.createEmoji.success.title(str(command_info.locale)), description=locale.commands.admin.createEmoji.success.description(str(command_info.locale), emoji=str(emoji), name=name, roles=roles_mention))
        await command_info.reply(embed=embed)
    except (TimeoutError, aiohttp.ClientError):
        await command_info.reply(locale.commands.admin.createEmoji.imageDownloadError(str(command_info.locale)))
    except discord.HTTPException as e:
        await command_info.reply(locale.commands.admin.createEmoji.error(str(command_info.locale), error=str(e)))