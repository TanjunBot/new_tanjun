"""
BoosterService: Consolidate booster channel/role CRUD into a single service.

Consolidates 10 loose functions from api.py (add_booster_channel, delete_booster_channel,
get_booster_channel, claim_booster_channel, remove_claimed_booster_channel,
get_claimed_booster_channel, add_booster_role, get_booster_role, delete_booster_role,
add_claimed_booster_role, remove_claimed_booster_role, get_claimed_booster_role)
into a single BoosterService class with Pydantic-validated parameter models.

Fixes the get_claimed_* anti-pattern where the return type was str | list[Model] | None
depending on parameters — split into typed methods.
"""

from __future__ import annotations

from enum import Enum

from api import execute_action, execute_query, safe_execute_query
from models import ClaimedBoosterChannelModel, ClaimedBoosterRoleModel
from utils.cache import StampedeProtectedCache

_claimed_all_cache: StampedeProtectedCache[str, list] = StampedeProtectedCache(ttl=30, maxsize=8)


def clear_booster_read_cache() -> None:
    _claimed_all_cache.clear()


class BoosterType(Enum):
    """Primary booster entity tables."""

    CHANNEL = "booster_channel"
    ROLE = "boosterRole"


class ClaimedBoosterType(Enum):
    """Claimed booster entity tables."""

    CHANNEL = "claimedBoosterChannel"
    ROLE = "claimedBoosterRole"


class BoosterService:
    """Consolidated CRUD for booster channels and roles.

    Usage:
        service = BoosterService()
        await service.add(BoosterType.CHANNEL, guild_id="123", entity_id="456")
        channel_id = await service.get(BoosterType.CHANNEL, guild_id="123")
        await service.claim(ClaimedBoosterType.CHANNEL, user_id="789", entity_id="456", guild_id="123")
    """

    # ------------------------------------------------------------------ #
    # Primary entity operations (booster_channel, boosterRole)
    # ------------------------------------------------------------------ #

    async def add(self, booster_type: BoosterType, guild_id: str, entity_id: str) -> None:
        """Insert a booster channel or role for a guild."""
        id_column = "channel_id" if booster_type == BoosterType.CHANNEL else "role_id"
        query = f"INSERT INTO {booster_type.value} (guild_id, {id_column}) VALUES (%s, %s)"
        await execute_action(query, (guild_id, entity_id))

    async def get(self, booster_type: BoosterType, guild_id: str) -> str | None:
        """Get the entity_id for a booster channel or role in a guild."""
        id_column = "channel_id" if booster_type == BoosterType.CHANNEL else "role_id"
        query = f"SELECT {id_column} FROM {booster_type.value} WHERE guild_id = %s"
        result = await execute_query(query, (guild_id,))
        return result[0][0] if result else None

    async def delete(self, booster_type: BoosterType, guild_id: str, entity_id: str | None = None) -> None:
        """Delete a booster channel or role.

        For CHANNEL type, entity_id is required (DELETE with both guild_id and channel_id).
        For ROLE type, entity_id is optional (DELETE with just guild_id).
        """
        if booster_type == BoosterType.CHANNEL:
            if entity_id is None:
                raise ValueError("entity_id is required for channel deletion")
            query = f"DELETE FROM {booster_type.value} WHERE guild_id = %s AND channel_id = %s"
            await execute_action(query, (guild_id, entity_id))
        else:
            query = f"DELETE FROM {booster_type.value} WHERE guild_id = %s"
            await execute_action(query, (guild_id,))

    # ------------------------------------------------------------------ #
    # Claimed entity operations (claimedBoosterChannel, claimedBoosterRole)
    # ------------------------------------------------------------------ #

    async def claim(
        self,
        claimed_type: ClaimedBoosterType,
        user_id: str,
        entity_id: str,
        guild_id: str,
    ) -> None:
        """Insert a claimed booster channel or role for a user."""
        id_column = "channel_id" if claimed_type == ClaimedBoosterType.CHANNEL else "role_id"
        query = f"INSERT INTO {claimed_type.value} (user_id, {id_column}, guild_id) VALUES (%s, %s, %s)"
        await execute_action(query, (user_id, entity_id, guild_id))
        _claimed_all_cache.invalidate(claimed_type.name)

    async def unclaim(
        self,
        claimed_type: ClaimedBoosterType,
        user_id: str,
        guild_id: str,
    ) -> None:
        """Remove a claimed booster channel or role for a user."""
        query = f"DELETE FROM {claimed_type.value} WHERE user_id = %s AND guild_id = %s"
        await execute_action(query, (user_id, guild_id))
        _claimed_all_cache.invalidate(claimed_type.name)

    async def get_claim_for_user(
        self,
        claimed_type: ClaimedBoosterType,
        user_id: str,
        guild_id: str,
    ) -> str | None:
        """Get a single claimed entity id for a user in a specific guild.

        Returns the entity_id (channel_id or role_id) for the user in the guild, or None if no claim exists.
        """
        id_column = "channel_id" if claimed_type == ClaimedBoosterType.CHANNEL else "role_id"
        query = f"SELECT {id_column} FROM {claimed_type.value} WHERE user_id = %s AND guild_id = %s"
        result = await safe_execute_query(query, (user_id, guild_id))
        return result[0][0] if result else None

    async def has_claim(
        self,
        claimed_type: ClaimedBoosterType,
        user_id: str,
    ) -> bool:
        """Check if a user has any claim of the given type across all guilds.

        Returns True if the user has at least one claim, False otherwise.
        """
        query = f"SELECT 1 FROM {claimed_type.value} WHERE user_id = %s LIMIT 1"
        result = await safe_execute_query(query, (user_id,))
        return bool(result)

    async def get_user_claims(
        self,
        claimed_type: ClaimedBoosterType,
        user_id: str,
    ) -> list:
        """Get all claimed booster entities for a user as model instances."""
        if claimed_type == ClaimedBoosterType.CHANNEL:
            query = "SELECT user_id, channel_id, guild_id FROM claimedBoosterChannel WHERE user_id = %s"
            result = await safe_execute_query(query, (user_id,))
            return [ClaimedBoosterChannelModel.from_row(row) for row in result]
        else:
            query = "SELECT user_id, role_id, guild_id FROM claimedBoosterRole WHERE user_id = %s"
            result = await safe_execute_query(query, (user_id,))
            return [ClaimedBoosterRoleModel.from_row(row) for row in result]

    async def _fetch_all_claims_from_db(self, claimed_type: ClaimedBoosterType) -> list:
        if claimed_type == ClaimedBoosterType.CHANNEL:
            query = "SELECT user_id, channel_id, guild_id FROM claimedBoosterChannel"
            result = await safe_execute_query(query)
            return [ClaimedBoosterChannelModel.from_row(row) for row in result]
        query = "SELECT user_id, role_id, guild_id FROM claimedBoosterRole"
        result = await safe_execute_query(query)
        return [ClaimedBoosterRoleModel.from_row(row) for row in result]

    async def get_all_claims(
        self,
        claimed_type: ClaimedBoosterType,
    ) -> list:
        """Get all claimed booster entities as model instances."""

        async def fetch() -> list:
            rows = await self._fetch_all_claims_from_db(claimed_type)
            return rows if rows is not None else []

        result: list | None = await _claimed_all_cache.get_or_fetch(claimed_type.name, fetch)
        if result is not None:
            return result
        _claimed_all_cache.invalidate(claimed_type.name)
        return await fetch()


# ------------------------------------------------------------------ #
# Singleton instance for easy import
# ------------------------------------------------------------------ #

booster_service = BoosterService()
