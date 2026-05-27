import discord

from api import (
    get_custom_formula,
    get_level_system_status,
    get_xp_scaling,
    update_user_xp_from_voice,
)
from loops._voice_tracker import voice_user_ids
from minigames._xp_core import calculate_xp, is_entity_blacklisted


def _get_member(client: discord.Client, user_id: int, guild_id: int) -> discord.Member | None:
    guild = client.get_guild(guild_id)
    if guild is None:
        return None
    return guild.get_member(user_id)


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
    for user_id, guild_id in list(voice_user_ids):
        user = _get_member(client, user_id, guild_id)
        if user is None:
            continue

        if not await get_level_system_status(user.guild.id):
            continue

        role_ids = {str(role.id) for role in user.roles}
        if await is_entity_blacklisted(
            str(user.guild.id),
            str(user.id),
            str(user.voice.channel.id) if user.voice and user.voice.channel else "0",
            role_ids,
        ):
            continue

        scaling, custom_formula, xp_to_add = await fetch_xp_details(user)
        await update_user_xp_from_voice(user.guild.id, user.id, xp_to_add, True)
