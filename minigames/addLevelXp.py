import discord
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
from utility import checkIfHasPro
import math
import random
from utility import get_level_for_xp


async def addLevelXp(message: discord.Message):
    if message.author.bot:
        return

    if not get_level_system_status(str(message.guild.id)):
        return

    # Check if the user has opted out of message tracking
    if check_if_opted_out(str(message.author.id)):
        return

    # Check blacklist
    if is_blacklisted(message):
        return

    scaling = get_xp_scaling(str(message.guild.id))
    custom_formula = get_custom_formula(str(message.guild.id))

    # Calculate XP to add
    xp_to_add = calculate_xp(message)

    # Get current XP and level
    current_xp = get_user_xp(str(message.guild.id), str(message.author.id))
    current_level = get_level_for_xp(
        current_xp if current_xp else 0, scaling, custom_formula
    )

    # Add XP
    new_xp = current_xp if current_xp else 0 + xp_to_add if xp_to_add else 0
    new_level = get_level_for_xp(new_xp if new_xp else 0, scaling, custom_formula)

    # Update XP in database
    update_user_xp(str(message.guild.id), str(message.author.id), new_xp)

    # Check for level up
    if new_level > current_level:
        await handle_level_up(message, new_level)


def is_blacklisted(message: discord.Message) -> bool:
    blacklist = get_blacklist(str(message.guild.id))

    # Check if channel is blacklisted
    if str(message.channel.id) in [channel[0] for channel in blacklist["channels"]]:
        return True

    # Check if any of user's roles are blacklisted
    user_role_ids = [str(role.id) for role in message.author.roles]
    if any(
        role_id in user_role_ids for role_id in [role[0] for role in blacklist["roles"]]
    ):
        return True

    # Check if user is blacklisted
    if str(message.author.id) in [user[0] for user in blacklist["users"]]:
        return True

    return False


def calculate_xp(message: discord.Message) -> int:
    base_xp = random.randint(1, 3)
    user_boost = get_user_boost(str(message.guild.id), str(message.author.id))
    role_boosts = get_user_roles_boosts(
        str(message.guild.id), [str(role.id) for role in message.author.roles]
    )
    channel_boost = get_channel_boost(str(message.guild.id), str(message.channel.id))

    total_additive_boost = 0
    total_multiplicative_boost = 1

    if user_boost:
        if user_boost[1]:  # if additive
            total_additive_boost += user_boost[0] - 1
        else:
            total_multiplicative_boost *= user_boost[0]

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

    # Check if level up messages are enabled
    if get_levelup_message_status(guild_id):
        level_up_message = get_levelup_message(guild_id)
        if level_up_message:
            level_up_message = level_up_message.replace(
                "{user}", message.author.mention
            )
            level_up_message = level_up_message.replace("{level}", str(new_level))

            # Get the channel to send the level up message
            level_up_channel_id = get_levelup_channel(guild_id)
            if level_up_channel_id:
                channel = message.guild.get_channel(int(level_up_channel_id))
            else:
                channel = message.channel

            await channel.send(level_up_message)

    # Handle level roles
    if checkIfHasPro(guild_id):
        level_roles = get_level_roles(guild_id)
        roles_to_add = [
            role_id for level, role_id in level_roles.items() if level <= new_level
        ]

        for role_id in roles_to_add:
            role = message.guild.get_role(int(role_id))
            if role and role not in message.author.roles:
                try:
                    await message.author.add_roles(
                        role, reason=f"Reached level {new_level}"
                    )
                except discord.Forbidden:
                    print(
                        f"Bot doesn't have permission to add role {role.name} to {message.author.name}"
                    )
