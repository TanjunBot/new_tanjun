import math
import random

import discord

from api import (
    check_if_opted_out,
    get_blacklist,
    get_channel_boost,
    get_custom_formula,
    get_level_roles,
    get_level_system_status,
    get_levelup_channel,
    get_levelup_message,
    get_levelup_message_status,
    get_user_boost,
    get_user_roles_boosts,
    get_user_xp,
    get_xp_scaling,
    update_user_xp,
)
from localizer import tanjunLocalizer
from utility import get_level_for_xp  # , checkIfHasPro

notifiedUsers = []


async def addLevelXp(message: discord.Message) -> None:
    if message.author.bot or await check_if_opted_out(str(message.author.id)):
        return

    if (message.guild == None):
        return

    guild_id = str(message.guild.id)
    if not await get_level_system_status(guild_id):
        return

    if await is_blacklisted(message, guild_id):
        return

    scaling, custom_formula, xp_to_add = await fetch_xp_details(message, guild_id)

    current_xp = await get_user_xp(guild_id, str(message.author.id)) or 0
    current_level = get_level_for_xp(current_xp, scaling, custom_formula)

    new_xp = current_xp + xp_to_add
    new_level = get_level_for_xp(new_xp, scaling, custom_formula)

    await update_user_xp(guild_id, str(message.author.id), xp_to_add, respect_cooldown=True)
    if new_level > current_level:
        await handle_level_up(message, new_level)


async def is_blacklisted(message: discord.Message, guild_id: str) -> bool:
    blacklist = await get_blacklist(guild_id)
    user_id = str(message.author.id)
    channel_id = str(message.channel.id)
    user_role_ids = {str(role.id) for role in message.author.roles} if hasattr(message.author, "roles") else []

    return (
        channel_id in (channel[0] for channel in blacklist["channels"])
        or user_id in (user[0] for user in blacklist["users"])
        or any(role_id in user_role_ids for role_id in (role[0] for role in blacklist["roles"]))
    )


async def fetch_xp_details(message: discord.Message, guild_id: str) -> tuple[str, str | None, int]:
    scaling = await get_xp_scaling(guild_id)
    custom_formula = await get_custom_formula(guild_id)
    xp_to_add = await calculate_xp(message, guild_id)
    return scaling, custom_formula, xp_to_add


async def calculate_xp(message: discord.Message, guild_id: str) -> int:
    # nosec: B311
    base_xp = random.randint(1, 3)
    user_boost = await get_user_boost(guild_id, str(message.author.id))
    if not user_boost:
        user_boost = None
    role_boosts = await get_user_roles_boosts(guild_id, [str(role.id) for role in (message.author.roles if hasattr(message.author, "roles") else [])])
    if not role_boosts:
        role_boosts = []
    channel_boost = await get_channel_boost(guild_id, str(message.channel.id))
    if not channel_boost:
        channel_boost = None

    total_additive_boost = sum(boost[0] - 1 for boost in role_boosts if boost[1])
    total_multiplicative_boost = math.prod(boost[0] for boost in role_boosts if not boost[1])

    if user_boost:
        if user_boost[1]:  # if additive
            total_additive_boost += user_boost[0] - 1
        else:
            total_multiplicative_boost *= user_boost[0]

    if role_boosts:
        for role_boost in role_boosts:
            if role_boost[1]:  # if additive
                total_additive_boost += role_boost[0] - 1
            else:
                total_multiplicative_boost *= role_boost[0]

    if channel_boost:
        if channel_boost[1]:  # if additive
            total_additive_boost += channel_boost[0] - 1
        else:
            total_multiplicative_boost *= channel_boost[0]

    total_boost = (1 + total_additive_boost) * total_multiplicative_boost
    return int(base_xp * total_boost)


async def handle_level_up(message: discord.Message, new_level: int) -> None:
    if (message.guild == None):
        return
    guild_id = str(message.guild.id)
    if await get_levelup_message_status(guild_id) and message.author.id not in notifiedUsers:
        channel = await determine_levelup_channel(message, guild_id)
        await channel.send(await format_level_up_message(guild_id, message.author.mention, new_level, message.guild)) # type: ignore[attr-defined]
        notifiedUsers.append(message.author.id)

    await update_user_roles(message, new_level, guild_id)


def clearNotifiedUsers() -> None:
    global notifiedUsers
    notifiedUsers = []


async def determine_levelup_channel(message: discord.Message, guild_id: str) -> discord.abc.GuildChannel:
    level_up_channel_id = await get_levelup_channel(guild_id)
    channel: discord.abc.GuildChannel = message.guild.get_channel(int(level_up_channel_id)) if message.guild != None and level_up_channel_id != None else message.channel # type: ignore[assignment]
    return channel

async def format_level_up_message(guild_id: str, user_mention: str, new_level: int, guild: discord.Guild) -> str:
    level_up_message = await get_levelup_message(guild_id)
    if not level_up_message:
        level_up_message = tanjunLocalizer.localize(
            str(guild.preferred_locale) if hasattr(guild, "preferred_locale") else "en_US",
            "commands.level.defaultlevelupmessage",
        )
    return level_up_message.replace("{user}", user_mention).replace("{level}", str(new_level))


async def update_user_roles(message: discord.Message, new_level: int, guild_id: str) -> None:
    if (message.guild == None or not isinstance(message.author, discord.Member)):
        return
    level_roles = await get_level_roles(guild_id)
    for level, role_id in level_roles:
        if level <= new_level:
            role = message.guild.get_role(int(role_id))
            if role and role not in message.author.roles:
                try:
                    await message.author.add_roles(
                        role,
                        reason=tanjunLocalizer.localize(
                            (str(message.guild.preferred_locale) if hasattr(message.guild, "preferred_locale") else "en_US"),
                            "commands.level.updateuserroles.reason",
                            level=level,
                        ),
                    )
                except discord.Forbidden:
                    pass
        elif level > new_level:
            role = message.guild.get_role(int(role_id))
            if role and role in message.author.roles:
                try:
                    await message.author.remove_roles(role)
                except discord.Forbidden:
                    pass
