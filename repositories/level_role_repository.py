"""LevelRoleRepository: Consolidated CRUD for level role assignments."""

from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any

from models import LevelRoleModel, LevelRolesGroupModel


@dataclass
class LevelRoleRepository:
    """Repository for managing level roles.

    Encapsulates all level_role CRUD queries used by the bot.
    """

    async def assign(self, guild_id: str, role_id: str, level: int) -> None:
        """Assign a role to unlock at a given level."""
        from api import execute_action

        query = """
        INSERT INTO levelRole (guild_id, role_id, level)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE role_id = VALUES(role_id)
        """
        params = (guild_id, role_id, level)
        await execute_action(query, params)

    async def unassign(self, guild_id: str, role_id: str) -> None:
        """Remove a level role assignment."""
        from api import execute_action

        query = """
        DELETE FROM levelRole
        WHERE guild_id = %s AND role_id = %s
        """
        params = (guild_id, role_id)
        await execute_action(query, params)

    async def get_by_role(self, guild_id: str, role_id: str) -> int | None:
        """Get the level a role unlocks, or None if not assigned."""
        from api import execute_query

        query = "SELECT level FROM levelRole WHERE guild_id = %s AND role_id = %s"
        params = (guild_id, role_id)
        result = await execute_query(query, params)
        return result[0][0] if result else None

    async def get_all(self, guild_id: str) -> AsyncIterator[LevelRoleModel]:
        """Stream all level roles for a guild."""
        query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s"
        params = (guild_id,)
        async for row in LevelRoleModel.iter_rows(query, params):
            yield row

    async def get_grouped_by_level(self, guild_id: str) -> list[LevelRolesGroupModel]:
        """Get level roles grouped by level, ordered by level."""
        query = "SELECT level, role_id FROM levelRole WHERE guild_id = %s ORDER BY level"
        params = (guild_id,)
        groups: dict[int, list[str]] = {}
        async for row in LevelRoleModel.iter_rows(query, params):
            if row.level not in groups:
                groups[row.level] = []
            groups[row.level].append(row.role_id)
        return [LevelRolesGroupModel(level=level, role_ids=roles) for level, roles in groups.items()]

    async def get_roles_for_level(self, guild_id: str, level: int) -> list[str]:
        """Get all role IDs assigned to a specific level."""
        from api import execute_query

        query = "SELECT role_id FROM levelRole WHERE guild_id = %s AND level = %s"
        params = (guild_id, level)
        result = await execute_query(query, params)
        return [row[0] for row in result] if result else []

    @staticmethod
    def group_by_level(roles: list[LevelRoleModel]) -> list[LevelRolesGroupModel]:
        """Group flat role models by level.

        Reusable and testable grouping logic lifted from the old
        inline dict-gathering pattern.
        """
        groups: dict[int, list[str]] = {}
        for role in roles:
            if role.level not in groups:
                groups[role.level] = []
            groups[role.level].append(role.role_id)
        return [LevelRolesGroupModel(level=level, role_ids=ids) for level, ids in sorted(groups.items())]


# Module-level singleton for easy import in existing callers
level_role_repo = LevelRoleRepository()
