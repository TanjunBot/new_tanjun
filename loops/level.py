from api import (
    update_user_xp_from_voice,
    check_if_opted_out,
    get_level_system_status,
    get_blacklist,
    get_xp_scaling,
    get_custom_formula,
    get_user_boost,
    get_user_roles_boosts,
    get_channel_boost,
)
from minigames.addLevelXp import fetch_xp_details, is_blacklisted
import random
import math

voiceUsers = []


async def is_blacklisted(user) -> bool:
    blacklist = await get_blacklist(user.guild.id)
    user_id = str(user.id)
    channel_id = str(user.voice.channel.id)
    user_role_ids = {str(role.id) for role in user.roles}

    return (
        channel_id in (channel[0] for channel in blacklist["channels"])
        or user_id in (user[0] for user in blacklist["users"])
        or any(
            role_id in user_role_ids
            for role_id in (role[0] for role in blacklist["roles"])
        )
    )


async def fetch_xp_details(user):
    scaling = await get_xp_scaling(user.guild.id)
    custom_formula = await get_custom_formula(user.guild.id)
    xp_to_add = await calculate_xp(user)
    return scaling, custom_formula, xp_to_add


async def calculate_xp(user) -> int:
    base_xp = random.randint(1, 3)
    user_boost = await get_user_boost(user.guild.id, str(user.id))
    if not user_boost:
        user_boost = []
    role_boosts = await get_user_roles_boosts(
        user.guild.id, [str(role.id) for role in user.roles]
    )
    if not role_boosts:
        role_boosts = []
    channel_boost = await get_channel_boost(user.guild.id, str(user.id))
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


async def addXpToVoiceUsers(client):
    print("looping trough: ", voiceUsers)
    for user in voiceUsers:
        if not await get_level_system_status(user.guild.id):
            return

        if await is_blacklisted(user):
            return

        scaling, custom_formula, xp_to_add = await fetch_xp_details(user)
        await update_user_xp_from_voice(
            user.guild.id,
            user.id,
            xp_to_add,
            True
        )


async def handleVoiceChange(user, before, after):
    if await check_if_opted_out(user.id):
        return

    channel_members = after.channel.members if after.channel else []
    active_members = [member for member in channel_members if not (member.voice.self_mute or member.voice.self_deaf)]

    if len(active_members) < 2:
        for member in channel_members:
            removeVoiceUser(member)
    else:
        updateVoiceUsers(active_members)

def updateVoiceUsers(active_members):
    global voiceUsers
    current_users_set = set(voiceUsers)
    active_users_set = set(active_members)

    users_to_add = active_users_set - current_users_set
    users_to_remove = current_users_set - active_users_set

    for user in users_to_add:
        addVoiceUser(user)
    for user in users_to_remove:
        removeVoiceUser(user)

def addVoiceUser(user):
    if user not in voiceUsers:
        voiceUsers.append(user)

def removeVoiceUser(user):
    if user in voiceUsers:
        voiceUsers.remove(user)

