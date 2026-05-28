"""
TriggerMessageService: Encapsulate trigger message CRUD and matching logic.

Consolidates the loose trigger message functions from api.py (get_trigger_messages,
add_trigger_message, remove_trigger_message, get_trigger_message_channels,
get_trigger_messages_by_channel, add_trigger_message_channel,
remove_trigger_message_channel, is_trigger_message) plus matching logic from
commands/admin/trigger_messages/send.py into a single service class with
Pydantic-validated parameter models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated

from api import execute_action, execute_query, execute_query_iter
from models import TriggerMessageModel, TriggerMessageChannelModel

# ------------------------------------------------------------------ #
# Pydantic models
# ------------------------------------------------------------------ #


class TriggerMessageCreateParams(BaseModel):
    """Validated parameters for creating a new trigger message."""

    guild_id: str
    trigger: Annotated[str, Field(min_length=1, max_length=100)]
    response: Annotated[str, Field(min_length=1, max_length=1000)]
    case_sensitive: bool = False


class TriggerMessageChannelAddParams(BaseModel):
    """Validated parameters for adding a channel restriction to a trigger."""

    guild_id: str
    channel_id: str
    trigger_id: int


# ------------------------------------------------------------------ #
# Service class
# ------------------------------------------------------------------ #


class TriggerMessageService:
    """Service for managing trigger messages, channel restrictions, and matching."""

    # ------------------------------------------------------------------ #
    # CRUD
    # ------------------------------------------------------------------ #

    async def create(self, guild_id: str, trigger: str, response: str, case_sensitive: bool = False) -> None:
        """Create a new trigger message."""
        query = (
            "INSERT INTO triggerMessages (guild_id, `trigger`, response, case_sensitive) "
            "VALUES (%s, %s, %s, %s)"
        )
        params = (guild_id, trigger, response, case_sensitive)
        await execute_action(query, params)

    async def delete(self, guild_id: str, trigger_id: int) -> None:
        """Delete a trigger message by its ID (not the trigger text)."""
        query = "DELETE FROM triggerMessages WHERE guild_id = %s AND id = %s"
        params = (guild_id, trigger_id)
        await execute_action(query, params)

    async def get_all(self, guild_id: str) -> list[TriggerMessageModel]:
        """Get all trigger messages for a guild."""
        query = (
            "SELECT id, guild_id, `trigger`, response, case_sensitive "
            "FROM triggerMessages WHERE guild_id = %s"
        )
        params = (guild_id,)
        rows: list[TriggerMessageModel] = []
        async for row in TriggerMessageModel.iter_rows(query, params):
            rows.append(row)
        return rows

    # ------------------------------------------------------------------ #
    # Channel restrictions
    # ------------------------------------------------------------------ #

    async def add_channel(self, guild_id: str, channel_id: str, trigger_id: int) -> None:
        """Restrict a trigger message to a specific channel."""
        query = (
            "INSERT INTO triggerMessagesChannel (guild_id, channel_id, triggerId) "
            "VALUES (%s, %s, %s)"
        )
        params = (guild_id, channel_id, trigger_id)
        await execute_action(query, params)

    async def remove_channel(self, guild_id: str, channel_id: str, trigger_id: int) -> None:
        """Remove a channel restriction from a trigger message."""
        query = (
            "DELETE FROM triggerMessagesChannel "
            "WHERE guild_id = %s AND channel_id = %s AND triggerId = %s"
        )
        params = (guild_id, channel_id, trigger_id)
        await execute_action(query, params)

    async def get_trigger_channels(self, guild_id: str, trigger_id: int) -> list[TriggerMessageChannelModel]:
        """Get all channel restrictions for a specific trigger message."""
        query = (
            "SELECT guild_id, channel_id, triggerId "
            "FROM triggerMessagesChannel WHERE guild_id = %s AND triggerId = %s"
        )
        params = (guild_id, trigger_id)
        rows: list[TriggerMessageChannelModel] = []
        async for row in TriggerMessageChannelModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def get_channel_triggers(self, guild_id: str, channel_id: str) -> list[TriggerMessageChannelModel]:
        """Get all trigger message channel restrictions for a specific channel."""
        query = (
            "SELECT guild_id, channel_id, triggerId "
            "FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s"
        )
        params = (guild_id, channel_id)
        rows: list[TriggerMessageChannelModel] = []
        async for row in TriggerMessageChannelModel.iter_rows(query, params):
            rows.append(row)
        return rows

    # ------------------------------------------------------------------ #
    # Matching
    # ------------------------------------------------------------------ #

    async def match(self, guild_id: str, content: str, channel_id: str) -> TriggerMessageModel | None:
        """Find a trigger message that matches the given content in the given channel.

        Performs a LIKE query and double-checks case sensitivity via Python logic.
        Returns None if no match is found.
        """
        query = """
            SELECT t.id, t.guild_id, t.`trigger`, t.response, t.case_sensitive
            FROM triggerMessages t
            LEFT JOIN triggerMessagesChannel tc
                ON t.id = tc.triggerId AND t.guild_id = tc.guild_id
            WHERE t.guild_id = %s
              AND t.`trigger` LIKE %s
              AND (tc.channel_id = %s)
        """
        # Use %-based LIKE matching: %content%
        like_pattern = f"%{content}%"
        params = (guild_id, like_pattern, channel_id)
        result = await execute_query(query, params)
        result = result[0] if result and result[0] else None
        if not result:
            return None

        trigger_message = TriggerMessageModel.from_row(result)
        if trigger_message.case_sensitive:
            if content != trigger_message.trigger:
                return None
        else:
            if content.lower() != trigger_message.trigger.lower():
                return None
        return trigger_message


# ------------------------------------------------------------------ #
# Module-level singleton
# ------------------------------------------------------------------ #

trigger_message_service = TriggerMessageService()
