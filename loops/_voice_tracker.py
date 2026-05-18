"""Shared voice user tracker for level XP and giveaway voice time.

Both loops/level.py and loops/giveaway.py need to track which users are
currently in active voice channels. Previously each module maintained its
own copy of the voiceUsers list and all four management functions, causing
duplicate Discord API calls on every voice state update.
"""

import discord

from api import check_if_opted_out

voiceUsers: list[discord.Member] = []


async def handleVoiceChange(user: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
    if await check_if_opted_out(user.id):
        return

    channel_members = after.channel.members if after.channel else []
    active_members = [member for member in channel_members if not (member.voice.self_mute or member.voice.self_deaf)]

    if len(active_members) < 2:
        for member in channel_members:
            removeVoiceUser(member)
    else:
        updateVoiceUsers(active_members)


def updateVoiceUsers(active_members: list[discord.Member]) -> None:
    global voiceUsers
    current_users_set = set(voiceUsers)
    active_users_set = set(active_members)

    users_to_add = active_users_set - current_users_set
    users_to_remove = current_users_set - active_users_set

    for user in users_to_add:
        addVoiceUser(user)
    for user in users_to_remove:
        removeVoiceUser(user)


def addVoiceUser(user: discord.Member) -> None:
    if user not in voiceUsers:
        voiceUsers.append(user)


def removeVoiceUser(user: discord.Member) -> None:
    if user in voiceUsers:
        voiceUsers.remove(user)
