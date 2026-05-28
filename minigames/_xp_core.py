"""Shared XP calculation for both voice and message XP.

Provides a single canonical calculate_xp used by both loops/level.py and
minigames/add_level_xp.py.

Delegates to XpCalculator service for the actual boost formula.
The XpCalculator service class is also exported for direct use.
"""

from services.xp_calculator import XpCalculator, xp_calculator
from api import _get_cached_blacklist

# Re-export for callers that want to use the service directly
__all__ = ["XpCalculator", "xp_calculator", "calculate_xp", "is_entity_blacklisted"]


async def calculate_xp(guild_id: str, user_id: str, channel_id: str, role_ids: list[str]) -> int:
    """Calculate XP to add based on base random value and boosts.

    Delegates to XpCalculator service for the boost formula.
    """
    return await xp_calculator.calculate_xp(guild_id, user_id, role_ids, channel_id)


async def is_entity_blacklisted(guild_id: str, user_id: str, channel_id: str, role_ids: set[str]) -> bool:
    """Check if a user/channel/role combo is blacklisted for XP using cached data."""
    blacklist = await _get_cached_blacklist(guild_id)
    return (
        channel_id in (channel.entity_id for channel in blacklist["channels"])
        or user_id in (user.entity_id for user in blacklist["users"])
        or any(role_id in role_ids for role_id in (role.entity_id for role in blacklist["roles"]))
    )
