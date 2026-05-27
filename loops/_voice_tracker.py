"""Shared voice user tracker for level XP and giveaway voice time.

Both loops/level.py and loops/giveaway.py need to track which users are
currently in active voice channels. Previously each module maintained its
own copy of the voiceUsers list and all four management functions, causing
duplicate Discord API calls on every voice state update.
"""

import discord

from api import check_if_opted_out

# Store (user_id, guild_id) pairs instead of Member objects to prevent
# memory leaks from stale/disconnected member references. IDs are stable
# across Discord reconnections and provide O(1) lookup & removal.
voice_user_ids: set[tuple[int, int]] = set()


async def handleVoiceChange(user: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
    if await check_if_opted_out(user.id):
        return

    channel_members = after.channel.members if after.channel else []
    active_members = [member for member in channel_members if not (member.voice.self_mute or member.voice.self_deaf)]

    if len(active_members) < 2:
        for member in channel_members:
            removeVoiceUser(member.id, member.guild.id)
    else:
        updateVoiceUsers([(m.id, m.guild.id) for m in active_members])


def updateVoiceUsers(active_user_ids: list[tuple[int, int]]) -> None:
    global voice_user_ids
    current_set = voice_user_ids
    active_set = set(active_user_ids)

    users_to_add = active_set - current_set
    users_to_remove = current_set - active_set

    for user_id, guild_id in users_to_add:
        addVoiceUser(user_id, guild_id)
    for user_id, guild_id in users_to_remove:
        removeVoiceUser(user_id, guild_id)


def addVoiceUser(user_id: int, guild_id: int) -> None:
    voice_user_ids.add((user_id, guild_id))


def removeVoiceUser(user_id: int, guild_id: int) -> None:
    voice_user_ids.discard((user_id, guild_id))
