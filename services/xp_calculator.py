"""
XpCalculator service class: Single canonical XP calculation logic.

Consolidates the shared calculate_xp function from minigames/_xp_core.py
into a proper service class with typed injection of the XpBoostRepository.
This eliminates duplication and makes the calculation testable in isolation.
"""

from __future__ import annotations

import random

from api import BoostTarget, XpBoostRepository

class XpCalculator:
    """Service for calculating XP gains based on user, role, and channel boosts.

    Encapsulates the additive + multiplicative boost formula used by both
    message-based XP (add_level_xp.py) and voice-based XP (loops/level.py).
    """

    def __init__(self, boost_repo: XpBoostRepository | None = None) -> None:
        """Initialize with an optional boost repository (defaults to XpBoostRepository)."""
        self._boost_repo = boost_repo or XpBoostRepository

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    async def calculate_xp(
        self,
        guild_id: str,
        user_id: str,
        role_ids: list[str],
        channel_id: str,
    ) -> int:
        """Calculate XP to add based on base random value and boosts.

        Uses base random value (1-3) multiplied by the effective boost
        computed from user, role, and channel boosts.

        Args:
            guild_id: Discord guild (server) ID.
            user_id: Discord user ID.
            role_ids: List of Discord role IDs for the user.
            channel_id: Discord channel ID.

        Returns:
            Integer XP amount to grant.
        """
        # nosec: B311 — random.randint is acceptable for XP variance
        base_xp = random.randint(1, 3)
        effective_boost = await self.get_effective_boost(guild_id, user_id, role_ids, channel_id)
        return int(base_xp * effective_boost)

    async def get_effective_boost(
        self,
        guild_id: str,
        user_id: str,
        role_ids: list[str],
        channel_id: str,
    ) -> float:
        """Compute the total effective boost multiplier.

        Combines additive and multiplicative boosts from user, role, and
        channel sources into a single multiplier.

        Formula:
            total = (1 + sum_of_additive_boosts) * product_of_multiplicative_boosts

        Args:
            guild_id: Discord guild (server) ID.
            user_id: Discord user ID.
            role_ids: List of Discord role IDs for the user.
            channel_id: Discord channel ID.

        Returns:
            Float effective boost multiplier.
        """
        total_additive_boost = 0.0
        total_multiplicative_boost = 1.0

        # Role boosts
        role_boosts = await self._boost_repo.get_boosts_for_target(guild_id, role_ids) or []
        for boost in role_boosts:
            if boost.additive:
                total_additive_boost += boost.boost - 1
            else:
                total_multiplicative_boost *= boost.boost

        # User boost
        user_boost = await self._boost_repo.get_boost(guild_id, user_id)
        if user_boost:
            if user_boost.additive:
                total_additive_boost += user_boost.boost - 1
            else:
                total_multiplicative_boost *= user_boost.boost

        # Channel boost
        channel_boost = await self._boost_repo.get_boost(guild_id, channel_id, BoostTarget.CHANNEL)
        if channel_boost:
            if channel_boost.additive:
                total_additive_boost += channel_boost.boost - 1
            else:
                total_multiplicative_boost *= channel_boost.boost

        return (1.0 + total_additive_boost) * total_multiplicative_boost


# ------------------------------------------------------------------ #
# Module-level singleton
# ------------------------------------------------------------------ #

xp_calculator = XpCalculator()
