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

from typing import Annotated

from pydantic import BaseModel, Field

from api import execute_action, execute_query
from models import TriggerMessageChannelModel, TriggerMessageModel

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
        # Validate parameters using Pydantic model
        validated = TriggerMessageCreateParams(
            guild_id=guild_id, trigger=trigger, response=response, case_sensitive=case_sensitive
        )
        query = "INSERT INTO triggerMessages (guild_id, `trigger`, response, case_sensitive) VALUES (%s, %s, %s, %s)"
        params = (validated.guild_id, validated.trigger, validated.response, validated.case_sensitive)
        await execute_action(query, params)

    async def delete(self, guild_id: str, trigger_id: int) -> None:
        """Delete a trigger message by its ID (not the trigger text)."""
        query = "DELETE FROM triggerMessages WHERE guild_id = %s AND id = %s"
        params = (guild_id, trigger_id)
        await execute_action(query, params)

    async def get_all(self, guild_id: str) -> list[TriggerMessageModel]:
        """Get all trigger messages for a guild."""
        query = "SELECT id, guild_id, `trigger`, response, case_sensitive FROM triggerMessages WHERE guild_id = %s"
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
        # Validate parameters using Pydantic model
        validated = TriggerMessageChannelAddParams(guild_id=guild_id, channel_id=channel_id, trigger_id=trigger_id)
        query = "INSERT INTO triggerMessagesChannel (guild_id, channel_id, triggerId) VALUES (%s, %s, %s)"
        params = (validated.guild_id, validated.channel_id, validated.trigger_id)
        await execute_action(query, params)

    async def remove_channel(self, guild_id: str, channel_id: str, trigger_id: int) -> None:
        """Remove a channel restriction from a trigger message."""
        query = "DELETE FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s AND triggerId = %s"
        params = (guild_id, channel_id, trigger_id)
        await execute_action(query, params)

    async def get_trigger_channels(self, guild_id: str, trigger_id: int) -> list[TriggerMessageChannelModel]:
        """Get all channel restrictions for a specific trigger message."""
        query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND triggerId = %s"
        params = (guild_id, trigger_id)
        rows: list[TriggerMessageChannelModel] = []
        async for row in TriggerMessageChannelModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def get_channel_triggers(self, guild_id: str, channel_id: str) -> list[TriggerMessageChannelModel]:
        """Get all trigger message channel restrictions for a specific channel."""
        query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s"
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

        First checks for exact matches, then falls back to LIKE matching.
        Double-checks case sensitivity via Python logic.
        Returns None if no match is found.
        """
        # First try exact match
        exact_query = """
            SELECT t.id, t.guild_id, t.`trigger`, t.response, t.case_sensitive
            FROM triggerMessages t
            LEFT JOIN triggerMessagesChannel tc
                ON t.id = tc.triggerId AND t.guild_id = tc.guild_id
            WHERE t.guild_id = %s
              AND t.`trigger` = %s
              AND (tc.channel_id = %s)
        """
        exact_params = (guild_id, content, channel_id)
        exact_result = await execute_query(exact_query, exact_params)

        if exact_result and exact_result[0]:
            trigger_message = TriggerMessageModel.from_row(exact_result[0])
            if trigger_message.case_sensitive:
                if content == trigger_message.trigger:
                    return trigger_message
            else:
                if content.lower() == trigger_message.trigger.lower():
                    return trigger_message

        # Fall back to LIKE pattern matching
        like_query = """
            SELECT t.id, t.guild_id, t.`trigger`, t.response, t.case_sensitive
            FROM triggerMessages t
            LEFT JOIN triggerMessagesChannel tc
                ON t.id = tc.triggerId AND t.guild_id = tc.guild_id
            WHERE t.guild_id = %s
              AND t.`trigger` LIKE %s
              AND (tc.channel_id = %s)
        """
        like_pattern = f"%{content}%"
        like_params = (guild_id, like_pattern, channel_id)
        like_results = await execute_query(like_query, like_params)

        if not like_results:
            return None

        # Scan all results for exact match first
        for row in like_results:
            if not row:
                continue
            trigger_message = TriggerMessageModel.from_row(row)
            if trigger_message.case_sensitive:
                if content == trigger_message.trigger:
                    return trigger_message
            else:
                if content.lower() == trigger_message.trigger.lower():
                    return trigger_message

        # If no exact match found in LIKE results, return first partial match that passes case check
        for row in like_results:
            if not row:
                continue
            trigger_message = TriggerMessageModel.from_row(row)
            if trigger_message.case_sensitive:
                if trigger_message.trigger in content:
                    return trigger_message
            else:
                if trigger_message.trigger.lower() in content.lower():
                    return trigger_message

        return None


# ------------------------------------------------------------------ #
# Module-level singleton
# ------------------------------------------------------------------ #

trigger_message_service = TriggerMessageService()
