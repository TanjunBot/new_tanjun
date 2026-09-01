from locale_keys import locale
import asyncio
import contextlib
import discord
from api import _get_cached_config, check_if_opted_out, get_level_roles, get_level_system_status, get_levelup_channel, get_levelup_message, get_levelup_message_status, get_user_xp, update_user_xp
from minigames._xp_core import calculate_xp, is_entity_blacklisted
from utility import get_level_for_xp_async
notifiedUsers: set[int] = set()
_MAX_NOTIFIED_USERS = 10000

async def addLevelXp(message: discord.Message) -> None:
    if await check_if_opted_out(str(message.author.id)):
        return
    if message.guild is None:
        return
    guild_id = str(message.guild.id)
    if not await get_level_system_status(guild_id):
        return
    role_ids = {str(role.id) for role in message.author.roles} if hasattr(message.author, 'roles') else set()
    if await is_entity_blacklisted(guild_id, str(message.author.id), str(message.channel.id), role_ids):
        return
    scaling, custom_formula, xp_to_add = await fetch_xp_details(message, guild_id)
    current_xp = await get_user_xp(guild_id, str(message.author.id)) or 0
    current_level = await get_level_for_xp_async(current_xp, scaling, custom_formula)
    new_xp = current_xp + xp_to_add
    new_level = await get_level_for_xp_async(new_xp, scaling, custom_formula)
    await update_user_xp(guild_id, str(message.author.id), xp_to_add, respect_cooldown=True)
    if new_level > current_level:
        await handle_level_up(message, new_level)

async def fetch_xp_details(message: discord.Message, guild_id: str) -> tuple[str, str | None, int]:
    scaling_task = _get_cached_config(guild_id, 'scaling', 'medium')
    formula_task = _get_cached_config(guild_id, 'custom_formula')
    xp_task = calculate_xp(guild_id, str(message.author.id), str(message.channel.id), [str(role.id) for role in (message.author.roles if hasattr(message.author, 'roles') else [])])
    scaling, custom_formula, xp_to_add = await asyncio.gather(scaling_task, formula_task, xp_task)
    return (scaling, custom_formula, xp_to_add)

async def handle_level_up(message: discord.Message, new_level: int) -> None:
    if message.guild is None:
        return
    guild_id = str(message.guild.id)
    if await get_levelup_message_status(guild_id) and message.author.id not in notifiedUsers:
        channel = await determine_levelup_channel(message, guild_id)
        await channel.send(await format_level_up_message(guild_id, message.author.mention, new_level, message.guild))
        notifiedUsers.add(message.author.id)
        if len(notifiedUsers) > _MAX_NOTIFIED_USERS:
            notifiedUsers.pop()
    await update_user_roles(message, new_level, guild_id)

def clearNotifiedUsers(*args: object, **kwargs: object) -> None:
    global notifiedUsers
    notifiedUsers.clear()

async def determine_levelup_channel(message: discord.Message, guild_id: str) -> discord.abc.Messageable:
    level_up_channel_id = await get_levelup_channel(guild_id)
    if message.guild is not None and level_up_channel_id is not None:
        ch = message.guild.get_channel(int(level_up_channel_id))
        if isinstance(ch, discord.abc.Messageable):
            return ch
    return message.channel

async def format_level_up_message(guild_id: str, user_mention: str, new_level: int, guild: discord.Guild) -> str:
    level_up_message = await get_levelup_message(guild_id)
    if not level_up_message:
        level_up_message = locale.commands.level.defaultlevelupmessage(str(guild.preferred_locale) if hasattr(guild, 'preferred_locale') else 'en_US')
    return level_up_message.replace('{user}', user_mention).replace('{level}', str(new_level))

async def update_user_roles(message: discord.Message, new_level: int, guild_id: str) -> None:
    if message.guild is None or not isinstance(message.author, discord.Member):
        return
    async for lr in get_level_roles(guild_id):
        if lr.level <= new_level:
            role = message.guild.get_role(int(lr.role_id))
            if role and role not in message.author.roles:
                with contextlib.suppress(discord.Forbidden):
                    await message.author.add_roles(role, reason=locale.commands.level.updateuserroles.reason(str(message.guild.preferred_locale) if hasattr(message.guild, 'preferred_locale') else 'en_US', level=lr.level))
        elif lr.level > new_level:
            role = message.guild.get_role(int(lr.role_id))
            if role and role in message.author.roles:
                with contextlib.suppress(discord.Forbidden):
                    await message.author.remove_roles(role)