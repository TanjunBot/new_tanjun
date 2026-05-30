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
    status: str | None = None  # "PENDING" | "INVESTIGATING" | "ACTION_TAKEN" | "DISMISSED"


class ReportCreateParams(BaseModel):
    """Parameters for creating a new report."""

    guild_id: str
    user_id: str
    reporter_id: str
    reason: str
    is_moderator: bool = False


class ReportService:
    """Service for managing reports, blocked reporters, and report channels."""

    VALID_STATUSES = ("PENDING", "INVESTIGATING", "ACTION_TAKEN", "DISMISSED")

    # ------------------------------------------------------------------ #
    # Reports
    # ------------------------------------------------------------------ #

    @staticmethod
    async def create(params: ReportCreateParams) -> int | None:
        """Create a new report and return its ID."""
        if params.is_moderator:
            query = (
                "INSERT INTO reports "
                "(guild_id, user_id, reporterId, reason, status, accepted, accepted_at, acceptedBy) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            from datetime import datetime

            vals: tuple[Any, ...] = (
                params.guild_id,
                params.user_id,
                params.reporter_id,
                params.reason,
                "INVESTIGATING",
                1,
                datetime.now(),
                params.reporter_id,
            )
        else:
            query = (
                "INSERT INTO reports "
                "(guild_id, user_id, reporterId, reason, status) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            vals = (params.guild_id, params.user_id, params.reporter_id, params.reason, "PENDING")
        return await execute_insert_and_get_id(query, vals)

    @staticmethod
    async def get(filter_: ReportFilter) -> list[ReportModel]:
        """Get reports matching the given filter."""
        query = """
            SELECT id, guild_id, user_id, reporterId, reason,
                   UNIX_TIMESTAMP(created_at) as created_at,
                   status,
                   UNIX_TIMESTAMP(status_updated_at) as status_updated_at,
                   status_updated_by,
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
            query += " AND status = %s"
            params.append(filter_.status)

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
                   status,
                   UNIX_TIMESTAMP(status_updated_at) as status_updated_at,
                   status_updated_by,
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
    async def set_status(
        guild_id: str,
        report_id: int | str,
        status: str,
        updated_by: str | None = None,
    ) -> None:
        """Update the status of a report."""
        status_upper = status.upper()
        if status_upper not in ReportService.VALID_STATUSES:
            msg = f"Invalid status '{status}'. Must be one of {ReportService.VALID_STATUSES}"
            raise ValueError(msg)

        query = (
            "UPDATE reports SET status = %s, status_updated_at = NOW(), status_updated_by = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (status_upper, updated_by, guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def accept(guild_id: str, report_id: int | str, accepted_by: str | None = None) -> None:
        """Mark a report as accepted (and set status to INVESTIGATING)."""
        query = (
            "UPDATE reports SET accepted = 1, accepted_at = NOW(), acceptedBy = %s, "
            "status = 'INVESTIGATING', status_updated_at = NOW(), status_updated_by = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (accepted_by, accepted_by, guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def reject(guild_id: str, report_id: int | str, accepted_by: str | None = None) -> None:
        """Mark a report as rejected (and set status to DISMISSED)."""
        query = (
            "UPDATE reports SET accepted = 0, accepted_at = NOW(), acceptedBy = %s, resolved = 2, "
            "status = 'DISMISSED', status_updated_at = NOW(), status_updated_by = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (accepted_by, accepted_by, guild_id, report_id)
        await execute_action(query, params)

    @staticmethod
    async def resolve(guild_id: str, report_id: int | str, resolved_by: str | None = None) -> None:
        """Mark a report as resolved (ACTION_TAKEN)."""
        query = (
            "UPDATE reports SET resolved = 1, resolved_at = NOW(), resolvedBy = %s, "
            "status = 'ACTION_TAKEN', status_updated_at = NOW(), status_updated_by = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (resolved_by, resolved_by, guild_id, report_id)
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
