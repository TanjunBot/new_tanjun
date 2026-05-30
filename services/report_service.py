"""ReportService: Encapsulate report CRUD with typed filter parameters.

Consolidates module-level report functions from api.py into a single
ReportService class with Pydantic filter models.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

# Re-export core API functions that ReportService wraps
from api import execute_action, execute_insert_and_get_id, execute_query
from models import BlockedReporterModel, ReportModel


class ReportFilter(BaseModel):
    """Filter for querying reports."""

    guild_id: str
    user_id: str | None = None
    reporter_id: str | None = None
    status: str | None = None  # "PENDING" | "ACCEPTED" | "RESOLVED" | "REJECTED"


class ReportCreateParams(BaseModel):
    """Parameters for creating a new report."""

    guild_id: str
    user_id: str
    reporter_id: str
    reason: str
    is_moderator: bool = False


class ReportService:
    """Service for managing reports, blocked reporters, and report channels."""

    # ------------------------------------------------------------------ #
    # Reports
    # ------------------------------------------------------------------ #

    @staticmethod
    async def create(params: ReportCreateParams) -> int | None:
        """Create a new report and return its ID."""
        if params.is_moderator:
            query = (
                "INSERT INTO reports "
                "(guild_id, user_id, reporterId, reason, accepted, accepted_at, acceptedBy) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            from datetime import datetime

            vals: tuple[Any, ...] = (
                params.guild_id,
                params.user_id,
                params.reporter_id,
                params.reason,
                1,
                datetime.now(),
                params.reporter_id,
            )
        else:
            query = "INSERT INTO reports (guild_id, user_id, reporterId, reason) VALUES (%s, %s, %s, %s)"
            vals = (params.guild_id, params.user_id, params.reporter_id, params.reason)
        return await execute_insert_and_get_id(query, vals)

    @staticmethod
    async def get(filter_: ReportFilter) -> list[ReportModel]:
        """Get reports matching the given filter."""
        query = """
            SELECT id, guild_id, user_id, reporterId, reason,
                   UNIX_TIMESTAMP(created_at) as created_at,
                   accepted,
                   UNIX_TIMESTAMP(accepted_at) as accepted_at,
                   acceptedBy,
                   resolved,
                   UNIX_TIMESTAMP(resolved_at) as resolved_at,
                   resolvedBy
            FROM reports WHERE guild_id = %s
        """
        params: list[Any] = [filter_.guild_id]

        if filter_.user_id is not None:
            query += " AND user_id = %s"
            params.append(filter_.user_id)
        if filter_.reporter_id is not None:
            query += " AND reporterId = %s"
            params.append(filter_.reporter_id)
        if filter_.status is not None:
            if filter_.status == "PENDING":
                query += " AND accepted = 0 AND resolved = 0"
            elif filter_.status == "ACCEPTED":
                query += " AND accepted = 1"
            elif filter_.status == "RESOLVED":
                query += " AND resolved = 1"
            elif filter_.status == "REJECTED":
                query += " AND accepted = 0 AND resolved = 1"

        rows: list[ReportModel] = []
        async for row in ReportModel.iter_rows(query, tuple(params)):
            rows.append(row)
        return rows

    @staticmethod
    async def get_by_reporter(guild_id: str, reporter_id: str) -> list[ReportModel]:
        """Get all reports filed by a specific reporter."""
        query = """
            SELECT id, guild_id, user_id, reporterId, reason,
                   UNIX_TIMESTAMP(created_at) as created_at,
                   accepted,
                   UNIX_TIMESTAMP(accepted_at) as accepted_at,
                   acceptedBy,
                   resolved,
                   UNIX_TIMESTAMP(resolved_at) as resolved_at,
                   resolvedBy
            FROM reports WHERE guild_id = %s AND reporterId = %s
        """
        params = (guild_id, reporter_id)
        rows: list[ReportModel] = []
        async for row in ReportModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def accept(guild_id: str, report_id: int | str, accepted_by: str | None = None) -> None:
        """Mark a report as accepted."""
        query = "UPDATE reports SET accepted = 1, accepted_at = NOW(), acceptedBy = %s WHERE guild_id = %s AND id = %s"
        params = (accepted_by, guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def reject(guild_id: str, report_id: int | str, accepted_by: str | None = None) -> None:
        """Mark a report as rejected."""
        query = (
            "UPDATE reports SET accepted = 0, accepted_at = NOW(), acceptedBy = %s, resolved = 2 "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (accepted_by, guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def resolve(guild_id: str, report_id: int | str) -> None:
        """Mark a report as resolved."""
        query = "UPDATE reports SET resolved = 1, resolved_at = NOW() WHERE guild_id = %s AND id = %s"
        params = (guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def delete(guild_id: str, report_id: int | str) -> None:
        """Delete a report."""
        query = "DELETE FROM reports WHERE guild_id = %s AND id = %s"
        params = (guild_id, report_id)
        await execute_action(query, params)

    # ------------------------------------------------------------------ #
    # Blocked Reporters
    # ------------------------------------------------------------------ #

    @staticmethod
    async def block_reporter(guild_id: str, reporter_id: str) -> None:
        """Block a reporter from filing new reports."""
        query = "INSERT INTO blockedReporters (guild_id, user_id) VALUES (%s, %s)"
        params = (guild_id, reporter_id)
        await execute_action(query, params)

    @staticmethod
    async def unblock_reporter(guild_id: str, reporter_id: str) -> None:
        """Unblock a reporter."""
        query = "DELETE FROM blockedReporters WHERE guild_id = %s AND user_id = %s"
        params = (guild_id, reporter_id)
        await execute_action(query, params)

    @staticmethod
    async def get_blocked_reporters(guild_id: str) -> list[BlockedReporterModel]:
        """Get all blocked reporters for a guild."""
        query = "SELECT guild_id, user_id FROM blockedReporters WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[BlockedReporterModel] = []
        async for row in BlockedReporterModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def is_blocked(guild_id: str, reporter_id: str) -> bool:
        """Check if a reporter is blocked."""
        query = "SELECT 1 FROM blockedReporters WHERE guild_id = %s AND user_id = %s"
        params = (guild_id, reporter_id)
        result = await execute_query(query, params)
        return bool(result)

    # ------------------------------------------------------------------ #
    # Report Channel Config
    # ------------------------------------------------------------------ #

    @staticmethod
    async def set_channel(guild_id: str, channel_id: str) -> None:
        """Set the report channel for a guild."""
        query = "INSERT INTO reportchannel (guild_id, channel_id) VALUES (%s, %s)"
        params = (guild_id, channel_id)
        await execute_action(query, params)

    @staticmethod
    async def get_channel(guild_id: str) -> str | None:
        """Get the report channel ID for a guild, or None."""
        result = await execute_query("SELECT channel_id FROM reportchannel WHERE guild_id = %s", (guild_id,))
        return result[0][0] if result else None

    @staticmethod
    async def remove_channel(guild_id: str) -> None:
        """Remove the report channel configuration for a guild."""
        query = "DELETE FROM reportchannel WHERE guild_id = %s"
        params = (guild_id,)
        await execute_action(query, params)


# Module-level convenience instance
report_service = ReportService()
