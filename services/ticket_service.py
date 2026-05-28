"""
TicketService: Encapsulate ticket CRUD and close/open logic into a single service.

Consolidates the loose ticket functions from api.py (create_ticket_message,
delete_ticket_message, get_ticket_messages, open_ticket, close_ticket, etc.) into a
single TicketService class with Pydantic-validated parameter models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from api import execute_action, execute_insert_and_get_id, execute_query
from models import TicketMessageModel, TicketModel


# ------------------------------------------------------------------ #
# Pydantic models
# ------------------------------------------------------------------ #


class TicketMessageConfig(BaseModel):
    """Validated parameters for creating a ticket message config."""

    guild_id: str
    channel_id: str
    introduction: str | None = None
    ping_role: str | None = None
    name: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=1024)
    summary_channel_id: str | None = None


# ------------------------------------------------------------------ #
# TicketService
# ------------------------------------------------------------------ #


class TicketService:
    """Service for managing ticket message configs and ticket instances."""

    # ------------------------------------------------------------------ #
    # Ticket message config
    # ------------------------------------------------------------------ #

    @staticmethod
    async def create_config(params: TicketMessageConfig) -> int | None:
        """Create a new ticket message config and return its ID."""
        query = (
            "INSERT INTO ticketMessages "
            "(guild_id, channel_id, introduction, pingRole, name, description, summaryChannelId) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        vals = (
            params.guild_id,
            params.channel_id,
            params.introduction,
            params.ping_role,
            params.name,
            params.description,
            params.summary_channel_id,
        )
        return await execute_insert_and_get_id(query, vals)

    @staticmethod
    async def delete_config(guild_id: str, message_id: int) -> None:
        """Delete a ticket message config."""
        query = "DELETE FROM ticketMessages WHERE guild_id = %s AND id = %s"
        await execute_action(query, (guild_id, message_id))

    @staticmethod
    async def get_configs(guild_id: str) -> list[TicketMessageModel]:
        """Get all ticket message configs for a guild."""
        query = (
            "SELECT id, guild_id, channel_id, introduction, pingRole, "
            "name, description, summaryChannelId "
            "FROM ticketMessages WHERE guild_id = %s"
        )
        rows: list[TicketMessageModel] = []
        async for row in TicketMessageModel.iter_rows(query, (guild_id,)):
            rows.append(row)
        return rows

    @staticmethod
    async def get_config(ticket_message_id: int) -> TicketMessageModel | None:
        """Get a single ticket message config by ID."""
        query = (
            "SELECT id, guild_id, channel_id, introduction, pingRole, "
            "name, description, summaryChannelId "
            "FROM ticketMessages WHERE id = %s"
        )
        result = await execute_query(query, (ticket_message_id,))
        return TicketMessageModel.from_row(result[0]) if result else None

    # ------------------------------------------------------------------ #
    # Ticket operations
    # ------------------------------------------------------------------ #

    @staticmethod
    async def open(
        guild_id: str,
        opener_id: str,
        config_id: int,
        channel_id: str,
    ) -> None:
        """Open a new ticket instance."""
        query = (
            "INSERT INTO tickets (guild_id, openerId, ticketMessageId, channel_id) "
            "VALUES (%s, %s, %s, %s)"
        )
        await execute_action(query, (guild_id, opener_id, config_id, channel_id))

    @staticmethod
    async def close(guild_id: str, ticket_id: int) -> None:
        """Close a ticket instance."""
        query = (
            "UPDATE tickets SET closed = 1, closedAt = NOW(), closedBy = %s "
            "WHERE guild_id = %s AND id = %s"
        )
        await execute_action(query, (guild_id, ticket_id))

    @staticmethod
    async def get_tickets(guild_id: str) -> list[TicketModel]:
        """Get all tickets for a guild."""
        query = """
            SELECT guild_id, openerId,
                   UNIX_TIMESTAMP(openedAt) as openedAt,
                   closed,
                   UNIX_TIMESTAMP(closedAt) as closedAt,
                   closedBy, channel_id, ticketMessageId
            FROM tickets WHERE guild_id = %s
        """
        rows: list[TicketModel] = []
        async for row in TicketModel.iter_rows(query, (guild_id,)):
            rows.append(row)
        return rows

    @staticmethod
    async def get_by_config_and_channel(
        guild_id: str,
        config_id: int,
        channel_id: str,
    ) -> TicketModel | None:
        """Get a ticket by its config ID and channel ID."""
        query = """
            SELECT guild_id, openerId,
                   UNIX_TIMESTAMP(openedAt) as openedAt,
                   closed,
                   UNIX_TIMESTAMP(closedAt) as closedAt,
                   closedBy, channel_id, ticketMessageId
            FROM tickets
            WHERE guild_id = %s AND ticketMessageId = %s AND channel_id = %s
        """
        result = await execute_query(query, (guild_id, config_id, channel_id))
        return TicketModel.from_row(result[0]) if result else None

    @staticmethod
    async def get_by_channel(
        guild_id: str,
        channel_id: str,
    ) -> TicketModel | None:
        """Get a ticket by its channel ID."""
        query = """
            SELECT guild_id, openerId,
                   UNIX_TIMESTAMP(openedAt) as openedAt,
                   closed,
                   UNIX_TIMESTAMP(closedAt) as closedAt,
                   closedBy, channel_id, ticketMessageId
            FROM tickets
            WHERE guild_id = %s AND channel_id = %s
        """
        result = await execute_query(query, (guild_id, channel_id))
        return TicketModel.from_row(result[0]) if result else None


# ------------------------------------------------------------------ #
# Singleton instance
# ------------------------------------------------------------------ #

ticket_service = TicketService()
