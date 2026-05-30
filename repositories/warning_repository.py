"""WarningRepository: Consolidated CRUD for warning management."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime

from models import DetailedWarningModel, WarnConfigModel, WarningModel


@dataclass
class WarningRepository:
    """Repository for managing warnings and warning configuration."""

    async def add(
        self,
        guild_id: str | int,
        user_id: str | int,
        reason: str,
        created_by: str | int,
        expiration_date: datetime | None = None,
    ) -> int:
        """Add a warning and return its ID."""
        from api import execute_insert_and_get_id

        query = "INSERT INTO warnings (guild_id, user_id, reason, expires_at, created_by) VALUES (%s, %s, %s, %s, %s)"
        params = (guild_id, user_id, reason, expiration_date, created_by)
        warning_id = await execute_insert_and_get_id(query, params)
        return warning_id

    async def get_all(self, guild_id: str | int, user_id: str | int | None = None) -> AsyncIterator[WarningModel]:
        """Stream all active warnings for a guild (or a specific user)."""
        if user_id is not None:
            query = "SELECT id, guild_id, user_id, reason, created_at, expires_at, created_by, escalation_level FROM warnings WHERE guild_id = %s AND user_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
            params = (guild_id, user_id)
        else:
            query = "SELECT id, guild_id, user_id, reason, created_at, expires_at, created_by, escalation_level FROM warnings WHERE guild_id = %s AND (expires_at IS NULL OR expires_at > NOW())"
            params = (guild_id,)
        async for row in WarningModel.iter_rows(query, params):
            yield row

    async def get_detailed(self, guild_id: str | int, user_id: str | int) -> AsyncIterator[DetailedWarningModel]:
        """Stream detailed warnings for a specific user in a guild, ordered by creation date descending."""
        query = (
            "SELECT id, reason, created_at, expires_at, created_by "
            "FROM warnings WHERE guild_id = %s AND user_id = %s "
            "ORDER BY created_at DESC"
        )
        params = (guild_id, user_id)
        async for row in DetailedWarningModel.iter_rows(query, params):
            yield row

    async def remove(self, warning_id: int) -> None:
        """Remove a warning by ID."""
        from api import execute_action

        query = "DELETE FROM warnings WHERE id = %s"
        params = (warning_id,)
        await execute_action(query, params)

    async def set_config(
        self,
        guild_id: str | int,
        expiration_days: int,
        timeout_threshold: int,
        timeout_duration: int,
        kick_threshold: int,
        ban_threshold: int,
    ) -> None:
        """Set or update warning configuration for a guild."""
        from api import execute_action

        query = (
            "INSERT INTO warn_config (guild_id, expiration_days, "
            "timeout_threshold, timeout_duration, "
            "kick_threshold, ban_threshold) "
            "VALUES (%s, %s, %s, %s, %s, %s) "
            "ON DUPLICATE KEY UPDATE "
            "expiration_days = VALUES(expiration_days), "
            "timeout_threshold = VALUES(timeout_threshold), "
            "timeout_duration = VALUES(timeout_duration), "
            "kick_threshold = VALUES(kick_threshold), "
            "ban_threshold = VALUES(ban_threshold)"
        )
        params = (
            guild_id,
            expiration_days,
            timeout_threshold,
            timeout_duration,
            kick_threshold,
            ban_threshold,
        )
        await execute_action(query, params)

    async def get_config(self, guild_id: str | int) -> WarnConfigModel | None:
        """Get warning configuration for a guild."""
        from api import execute_query

        query = "SELECT guild_id, expiration_days, timeout_threshold, timeout_duration, kick_threshold, ban_threshold FROM warn_config WHERE guild_id = %s"
        params = (guild_id,)
        result = await execute_query(query, params)
        if result:
            return WarnConfigModel.from_row(result[0])
        return None


# Module-level singleton for easy import
warning_repo = WarningRepository()
