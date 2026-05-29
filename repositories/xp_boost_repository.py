"""XpBoostRepository: Consolidated CRUD for XP boost entries.

Replaces 9+ individual add/remove/get functions in api.py with
type-safe repository methods using BoostTarget enum.
"""

from __future__ import annotations

from enum import Enum
from models import XpBoostModel


class BoostTarget(Enum):
    """Type-safe enum for XP boost target types, mapping to DB table and entity column."""

    ROLE = ("roleXpBoost", "role_id")
    CHANNEL = ("channelXpBoost", "channel_id")
    USER = ("userXpBoost", "user_id")

    @property
    def table(self) -> str:
        return self.value[0]

    @property
    def entity_column(self) -> str:
        return self.value[1]


class XpBoostRepository:
    """Consolidated XP boost CRUD using BoostTarget enum.

    Replaces the 9+ individual add/remove/get functions for role, channel, and user boosts.
    """

    @staticmethod
    async def add_boost(
        guild_id: str,
        entity_id: str,
        boost: float,
        additive: bool,
        target: BoostTarget = BoostTarget.USER,
    ) -> None:
        """Add or update an XP boost entry."""
        from api import execute_action

        query = f"""
        INSERT INTO {target.table} (guild_id, {target.entity_column}, boost, additive)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE boost = VALUES(boost), additive = VALUES(additive)
        """
        params = (guild_id, entity_id, boost, additive)
        await execute_action(query, params)

    @staticmethod
    async def remove_boost(
        guild_id: str,
        entity_id: str,
        target: BoostTarget = BoostTarget.USER,
    ) -> None:
        """Remove an XP boost entry."""
        from api import execute_action

        query = f"DELETE FROM {target.table} WHERE guild_id = %s AND {target.entity_column} = %s"
        params = (guild_id, entity_id)
        await execute_action(query, params)

    @staticmethod
    async def get_boost(
        guild_id: str,
        entity_id: str,
        target: BoostTarget = BoostTarget.USER,
    ) -> XpBoostModel | None:
        """Get a specific XP boost entry by entity ID."""
        from api import execute_query

        query = f"SELECT boost, additive FROM {target.table} WHERE guild_id = %s AND {target.entity_column} = %s"
        params = (guild_id, entity_id)
        result = await execute_query(query, params)
        return XpBoostModel.from_row(result[0]) if result else None

    @staticmethod
    async def get_boosts_for_target(
        guild_id: str,
        entity_ids: list[str],
        target: BoostTarget = BoostTarget.ROLE,
    ) -> list[XpBoostModel]:
        """Get all boost entries for a list of entity IDs under a target type."""
        if not entity_ids:
            return []
        query = f"SELECT boost, additive FROM {target.table} WHERE guild_id = %s AND {target.entity_column} IN %s"
        params = (guild_id, tuple(entity_ids))
        rows: list[XpBoostModel] = []
        async for row in XpBoostModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def get_all_boosts(guild_id: str) -> dict[str, list[XpBoostModel]]:
        """Get all boosts for a guild, grouped by target type."""
        role_query = "SELECT boost, additive FROM roleXpBoost WHERE guild_id = %s"
        channel_query = "SELECT boost, additive FROM channelXpBoost WHERE guild_id = %s"
        user_query = "SELECT boost, additive FROM userXpBoost WHERE guild_id = %s"

        roles: list[XpBoostModel] = []
        async for row in XpBoostModel.iter_rows(role_query, (guild_id,)):
            roles.append(row)

        channels: list[XpBoostModel] = []
        async for row in XpBoostModel.iter_rows(channel_query, (guild_id,)):
            channels.append(row)

        users: list[XpBoostModel] = []
        async for row in XpBoostModel.iter_rows(user_query, (guild_id,)):
            users.append(row)

        return {
            "roles": roles,
            "channels": channels,
            "users": users,
        }


# Module-level singleton for easy import
xp_boost_repo = XpBoostRepository()
