import discord
import random
import math
from api import (
    get_user_xp,
    update_user_xp,
    get_level_roles,
    get_blacklist,
    get_levelup_message_status,
    get_levelup_message,
    get_levelup_channel,
    get_xp_scaling,
    get_custom_formula,
    check_if_opted_out,
    get_level_system_status,
    get_user_boost,
    get_user_roles_boosts,
    get_channel_boost,
)
from utility import checkIfHasPro, get_level_for_xp
from localizer import tanjunLocalizer

notifiedUsers = []

async def addLevelXp(message: discord.Message):
    if message.author.bot or await check_if_opted_out(str(message.author.id)):
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
    user_role_ids = {str(role.id) for role in message.author.roles}

    return (
        channel_id in (channel[0] for channel in blacklist["channels"])
        or user_id in (user[0] for user in blacklist["users"])
        or any(
            role_id in user_role_ids
            for role_id in (role[0] for role in blacklist["roles"])
        )
    )


async def fetch_xp_details(message: discord.Message, guild_id: str):
    scaling = await get_xp_scaling(guild_id)
    custom_formula = await get_custom_formula(guild_id)
    xp_to_add = await calculate_xp(message, guild_id)
    return scaling, custom_formula, xp_to_add


async def calculate_xp(message: discord.Message, guild_id: str) -> int:
    #nosec: B311
    base_xp = random.randint(1, 3)
    user_boost = await get_user_boost(guild_id, str(message.author.id))
    if not user_boost:
        user_boost = []
    role_boosts = await get_user_roles_boosts(
        guild_id, [str(role.id) for role in message.author.roles]
    )
    if not role_boosts:
        role_boosts = []
    channel_boost = await get_channel_boost(guild_id, str(message.channel.id))
    if not channel_boost:
        channel_boost = []

    total_additive_boost = sum(boost[0] - 1 for boost in role_boosts if boost[1])
    total_multiplicative_boost = math.prod(
        boost[0] for boost in role_boosts if not boost[1]
    )

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


async def handle_level_up(message: discord.Message, new_level: int):
    guild_id = str(message.guild.id)
    if await get_levelup_message_status(guild_id) and message.author.id not in notifiedUsers:
        channel = await determine_levelup_channel(message, guild_id)
        await channel.send(
            await format_level_up_message(guild_id, message.author.mention, new_level, message.guild)
        )
        notifiedUsers.append(message.author.id)

    await update_user_roles(message, new_level, guild_id)

def clearNotifiedUsers():
    global notifiedUsers
    notifiedUsers = []

async def determine_levelup_channel(
    message: discord.Message, guild_id: str
) -> discord.TextChannel:
    level_up_channel_id = await get_levelup_channel(guild_id)
    return (
        message.guild.get_channel(int(level_up_channel_id))
        if level_up_channel_id
        else message.channel
    )


async def format_level_up_message(
    guild_id: str, user_mention: str, new_level: int, guild: discord.Guild
) -> str:
    level_up_message = await get_levelup_message(guild_id)
    if not level_up_message:
        level_up_message = tanjunLocalizer.localize(
            guild.locale if hasattr(guild, "locale") else "en_US",
            "commands.level.defaultLevelUpMessage"
        )
    return level_up_message.replace("{user}", user_mention).replace(
        "{level}", str(new_level)
    )


async def update_user_roles(message: discord.Message, new_level: int, guild_id: str):
    level_roles = await get_level_roles(guild_id, new_level)
    roles_to_add = [
        role_id for role_id in level_roles
    ]
    for role_id in roles_to_add:
        role = message.guild.get_role(int(role_id))
        if role and role not in message.author.roles:
            try:
                await message.author.add_roles(
                    role, reason=f"Reached level {new_level}"
                )
            except:
                pass