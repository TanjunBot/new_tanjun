"""ReportService: Encapsulate report CRUD with typed filter parameters.

Consolidates and extends module-level report functions from api.py into a single
ReportService class with Pydantic filter models, evidence upload, status transitions,
notifications, moderation linking, and anonymity toggle.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel

# Re-export core API functions that ReportService wraps
from api import execute_action, execute_insert_and_get_id, execute_query
from models import BlockedReporterModel, ReportEvidenceModel, ReportModel, ReportModActionModel


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


class ReportNotifyParams(BaseModel):
    """Parameters for sending a status-change notification to a reporter."""
    guild_id: str
    report_id: int
    reporter_id: str
    old_status: str
    new_status: str
    note: str | None = None


class ReportService:
    """Service for managing reports, blocked reporters, report channels, evidence,
    moderation actions, notifications, and anonymity settings."""

    # ------------------------------------------------------------------ #
    # Reports
    # ------------------------------------------------------------------ #

    @staticmethod
    async def create(params: ReportCreateParams) -> int | None:
        """Create a new report with explicit status and return its ID."""
        from api import execute_query

        if params.is_moderator:
            query = (
                "INSERT INTO reports "
                "(guild_id, user_id, reporterId, reason, status, accepted, accepted_at, acceptedBy) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            )
            vals: tuple[Any, ...] = (
                params.guild_id,
                params.user_id,
                params.reporter_id,
                params.reason,
                "investigating",
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
            vals = (params.guild_id, params.user_id, params.reporter_id, params.reason, "pending")
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
                   status_note,
                   anonymous
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
                   status_note,
                   anonymous
            FROM reports WHERE guild_id = %s AND reporterId = %s
        """
        params = (guild_id, reporter_id)
        rows: list[ReportModel] = []
        async for row in ReportModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def get_by_id(guild_id: str, report_id: int | str) -> ReportModel | None:
        """Get a single report by ID."""
        query = """
            SELECT id, guild_id, user_id, reporterId, reason,
                   UNIX_TIMESTAMP(created_at) as created_at,
                   status,
                   UNIX_TIMESTAMP(status_updated_at) as status_updated_at,
                   status_updated_by,
                   status_note,
                   anonymous
            FROM reports WHERE guild_id = %s AND id = %s
        """
        params = (guild_id, int(report_id))
        async for row in ReportModel.iter_rows(query, params):
            return row
        return None

    @staticmethod
    async def update_status(
        guild_id: str,
        report_id: int | str,
        new_status: str,
        updated_by: str | None = None,
        note: str | None = None,
    ) -> str | None:
        """Update report status. Returns the previous status or None if not found."""
        # Get current status first
        current = await execute_query(
            "SELECT status FROM reports WHERE guild_id = %s AND id = %s",
            (guild_id, int(report_id)),
        )
        if not current:
            return None
        old_status = current[0][0]

        query = (
            "UPDATE reports SET status = %s, status_updated_at = NOW(), "
            "status_updated_by = %s, status_note = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        params = (new_status, updated_by, note, guild_id, int(report_id))
        await execute_action(query, params)
        return old_status

    @staticmethod
    async def set_anonymous(guild_id: str, report_id: int | str, anonymous: bool) -> None:
        """Set the anonymity flag on a report."""
        query = "UPDATE reports SET anonymous = %s WHERE guild_id = %s AND id = %s"
        params = (int(anonymous), guild_id, int(report_id))
        await execute_action(query, params)

    @staticmethod
    async def delete(guild_id: str, report_id: int | str) -> None:
        """Delete a report and its associated evidence."""
        await execute_action(
            "DELETE FROM report_evidence WHERE report_id = %s AND guild_id = %s",
            (int(report_id), guild_id),
        )
        await execute_action(
            "DELETE FROM report_mod_actions WHERE report_id = %s AND guild_id = %s",
            (int(report_id), guild_id),
        )
        await execute_action(
            "DELETE FROM reports WHERE guild_id = %s AND id = %s",
            (guild_id, int(report_id)),
        )

    # ------------------------------------------------------------------ #
    # Evidence
    # ------------------------------------------------------------------ #

    @staticmethod
    async def add_evidence(
        guild_id: str,
        report_id: int | str,
        url: str,
        filename: str | None = None,
        uploaded_by: str | None = None,
    ) -> int | None:
        """Add evidence (file URL) to a report."""
        query = (
            "INSERT INTO report_evidence "
            "(guild_id, report_id, url, filename, uploaded_by) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        vals = (guild_id, int(report_id), url, filename, uploaded_by)
        return await execute_insert_and_get_id(query, vals)

    @staticmethod
    async def get_evidence(guild_id: str, report_id: int | str) -> list[ReportEvidenceModel]:
        """Get all evidence for a report."""
        query = (
            "SELECT id, guild_id, report_id, url, filename, uploaded_by, "
            "UNIX_TIMESTAMP(uploaded_at) as uploaded_at "
            "FROM report_evidence WHERE guild_id = %s AND report_id = %s "
            "ORDER BY uploaded_at ASC"
        )
        params = (guild_id, int(report_id))
        rows: list[ReportEvidenceModel] = []
        async for row in ReportEvidenceModel.iter_rows(query, params):
            rows.append(row)
        return rows

    @staticmethod
    async def delete_evidence(guild_id: str, evidence_id: int | str) -> None:
        """Delete a specific evidence entry."""
        query = "DELETE FROM report_evidence WHERE guild_id = %s AND id = %s"
        params = (guild_id, int(evidence_id))
        await execute_action(query, params)

    # ------------------------------------------------------------------ #
    # Moderation Action Linking
    # ------------------------------------------------------------------ #

    @staticmethod
    async def add_mod_action(
        guild_id: str,
        report_id: int | str,
        action_type: str,
        target_id: str,
        performed_by: str,
        details: str | None = None,
    ) -> int | None:
        """Record a moderation action linked to a report.

        action_type: 'ban', 'kick', 'timeout', 'warning', 'note'
        """
        query = (
            "INSERT INTO report_mod_actions "
            "(guild_id, report_id, action_type, target_id, performed_by, details) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        vals = (guild_id, int(report_id), action_type, target_id, performed_by, details)
        return await execute_insert_and_get_id(query, vals)

    @staticmethod
    async def get_mod_actions(guild_id: str, report_id: int | str) -> list[ReportModActionModel]:
        """Get all moderation actions linked to a report."""
        query = (
            "SELECT id, guild_id, report_id, action_type, target_id, performed_by, details, "
            "UNIX_TIMESTAMP(created_at) as created_at "
            "FROM report_mod_actions WHERE guild_id = %s AND report_id = %s "
            "ORDER BY created_at ASC"
        )
        params = (guild_id, int(report_id))
        rows: list[ReportModActionModel] = []
        async for row in ReportModActionModel.iter_rows(query, params):
            rows.append(row)
        return rows

    # ------------------------------------------------------------------ #
    # Anonymity Guild Setting
    # ------------------------------------------------------------------ #

    @staticmethod
    async def set_anonymity_setting(guild_id: str, enabled: bool) -> None:
        """Enable or disable anonymous-by-default for a guild."""
        # Upsert
        result = await execute_query(
            "SELECT guild_id FROM report_anonymity WHERE guild_id = %s",
            (guild_id,),
        )
        if result:
            await execute_action(
                "UPDATE report_anonymity SET enabled = %s WHERE guild_id = %s",
                (int(enabled), guild_id),
            )
        else:
            await execute_action(
                "INSERT INTO report_anonymity (guild_id, enabled) VALUES (%s, %s)",
                (guild_id, int(enabled)),
            )

    @staticmethod
    async def get_anonymity_setting(guild_id: str) -> bool:
        """Check if anonymous reports are enabled by default for a guild."""
        result = await execute_query(
            "SELECT enabled FROM report_anonymity WHERE guild_id = %s",
            (guild_id,),
        )
        return bool(result[0][0]) if result else False

    # ------------------------------------------------------------------ #
    # Notification Tracking
    # ------------------------------------------------------------------ #

    @staticmethod
    async def has_opted_out_of_notifications(guild_id: str, reporter_id: str) -> bool:
        """Check if a reporter has opted out of status notifications."""
        result = await execute_query(
            "SELECT 1 FROM report_notification_optout WHERE guild_id = %s AND user_id = %s",
            (guild_id, reporter_id),
        )
        return bool(result)

    @staticmethod
    async def set_notification_optout(guild_id: str, reporter_id: str, opted_out: bool) -> None:
        """Set notification opt-out for a reporter."""
        if opted_out:
            await execute_action(
                "INSERT INTO report_notification_optout (guild_id, user_id) VALUES (%s, %s)",
                (guild_id, reporter_id),
            )
        else:
            await execute_action(
                "DELETE FROM report_notification_optout WHERE guild_id = %s AND user_id = %s",
                (guild_id, reporter_id),
            )

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
