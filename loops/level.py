import discord

from api import (
    get_custom_formula,
    get_level_system_status,
    get_xp_scaling,
    update_user_xp_from_voice,
)
from loops._voice_tracker import voiceUsers
from minigames._xp_core import calculate_xp, is_entity_blacklisted


async def fetch_xp_details(user: discord.Member):
    scaling = await get_xp_scaling(user.guild.id)
    custom_formula = await get_custom_formula(user.guild.id)
    xp_to_add = await calculate_xp(
        str(user.guild.id),
        str(user.id),
        str(user.voice.channel.id) if user.voice and user.voice.channel else "0",
        [str(role.id) for role in user.roles],
    )
    return scaling, custom_formula, xp_to_add


async def addXpToVoiceUsers(client):
    for user in voiceUsers:
        if not await get_level_system_status(user.guild.id):
            continue

        role_ids = {str(role.id) for role in user.roles}
        if await is_entity_blacklisted(str(user.guild.id), str(user.id), str(user.voice.channel.id), role_ids):
            continue

        scaling, custom_formula, xp_to_add = await fetch_xp_details(user)
        await update_user_xp_from_voice(user.guild.id, user.id, xp_to_add, True)
