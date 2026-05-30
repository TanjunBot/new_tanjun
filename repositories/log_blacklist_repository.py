"""LogBlacklistRepository: Consolidated CRUD for log blacklist management."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LogBlacklistType(Enum):
    """Enum representing log blacklist types with their table/column mapping."""

    CHANNEL = ("logBlacklistChannel", "channel_id")
    ROLE = ("logRoleBlacklist", "role_id")
    USER = ("logUserBlacklist", "user_id")
    VOICE_CHANNEL = ("logVoiceBlacklist", "channel_id")
    CATEGORY = ("logCategoryBlacklist", "channel_id")

    @property
    def table(self) -> str:
        return self.value[0]

    @property
    def column(self) -> str:
        return self.value[1]


@dataclass
class LogBlacklistRepository:
    """Repository for managing log blacklist entries."""

    async def add(self, guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> None:
        """Add a log blacklist entry for the given entity type."""
        from api import execute_action

        table = blacklist_type.table
        column = blacklist_type.column
        query = f"INSERT INTO {table} (guild_id, {column}) VALUES (%s, %s)"
        await execute_action(query, (guild_id, entity_id))

    async def remove(self, guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> None:
        """Remove a log blacklist entry for the given entity type."""
        from api import execute_action

        table = blacklist_type.table
        column = blacklist_type.column
        query = f"DELETE FROM {table} WHERE guild_id = %s AND {column} = %s"
        await execute_action(query, (guild_id, entity_id))

    async def get_all(self, guild_id: str, blacklist_type: LogBlacklistType) -> list[str]:
        """Retrieve all blacklisted entity IDs of a given type for a guild."""
        from api import execute_query_iter

        table = blacklist_type.table
        column = blacklist_type.column
        query = f"SELECT {column} FROM {table} WHERE guild_id = %s"
        entity_ids: list[str] = []
        async for row in execute_query_iter(query, (guild_id,)):
            entity_ids.append(row[0])
        return entity_ids

    async def is_entity_blacklisted(self, guild_id: str, entity_id: str, blacklist_type: LogBlacklistType) -> str | None:
        """Check whether a specific entity is blacklisted."""
        from api import execute_query

        table = blacklist_type.table
        column = blacklist_type.column
        query = f"SELECT {column} FROM {table} WHERE guild_id = %s AND {column} = %s"
        result = await execute_query(query, (guild_id, entity_id))
        return result[0] if result else None


# Module-level singleton for easy import
log_blacklist_repo = LogBlacklistRepository()
