"""Shared XP calculation for both voice and message XP.

The calculate_xp function was duplicated between loops/level.py and
minigames/addLevelXp.py with nearly identical logic. This module provides
a single implementation that both can use.
"""

import math
import random

from api import _get_cached_blacklist, get_channel_boost, get_user_boost, get_user_roles_boosts


async def calculate_xp(guild_id: str, user_id: str, channel_id: str, role_ids: list[str]) -> int:
    """Calculate XP to add based on base random value and boosts."""
    # nosec: B311
    base_xp = random.randint(1, 3)
    user_boost = await get_user_boost(guild_id, user_id)
    role_boosts = await get_user_roles_boosts(guild_id, role_ids) or []
    channel_boost = await get_channel_boost(guild_id, channel_id)

    total_additive_boost = sum(boost.boost - 1 for boost in role_boosts if boost.additive)
    total_multiplicative_boost = math.prod(boost.boost for boost in role_boosts if not boost.additive)

    if user_boost:
        if user_boost.additive:
            total_additive_boost += user_boost.boost - 1
        else:
            total_multiplicative_boost *= user_boost.boost

    if role_boosts:
        for role_boost in role_boosts:
            if role_boost.additive:
                total_additive_boost += role_boost.boost - 1
            else:
                total_multiplicative_boost *= role_boost.boost

    if channel_boost:
        if channel_boost.additive:
            total_additive_boost += channel_boost.boost - 1
        else:
            total_multiplicative_boost *= channel_boost.boost

    total_boost = (1 + total_additive_boost) * total_multiplicative_boost
    return int(base_xp * total_boost)


async def is_entity_blacklisted(guild_id: str, user_id: str, channel_id: str, role_ids: set[str]) -> bool:
    """Check if a user/channel/role combo is blacklisted for XP using cached data."""
    blacklist = await _get_cached_blacklist(guild_id)
    return (
        channel_id in (channel.entity_id for channel in blacklist["channels"])
        or user_id in (user.entity_id for user in blacklist["users"])
        or any(role_id in role_ids for role_id in (role.entity_id for role in blacklist["roles"]))
    )
