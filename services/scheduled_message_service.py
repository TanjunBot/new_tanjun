"""
ScheduledMessageService: Encapsulate scheduled message CRUD with Pydantic params.

Consolidates the loose scheduled-message functions from api.py into a single
service with typed parameter models and clear method names.
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, StringConstraints

from models import ScheduledMessageModel
from tanjun_types import GuildId, ChannelId, UserId


class Attachment(BaseModel):
    """Validated attachment for scheduled messages."""

    filename: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    content_type: Annotated[str, StringConstraints(max_length=127)] | None = None
    size: Annotated[int, Field(ge=0, le=25_000_000)] = 0  # Max 25MB per attachment
    url: Annotated[str, StringConstraints(max_length=2048)]


class ScheduleMessageParams(BaseModel):
    """Validated parameters for scheduling a new message."""

    guild_id: GuildId | None = None
    channel_id: ChannelId | None = None
    user_id: UserId
    content: Annotated[str, StringConstraints(max_length=1024)]
    send_time: datetime
    repeat_interval: int | None = Field(default=None, ge=0)
    repeat_amount: int | None = Field(default=None, ge=0)
    attachments: Annotated[list[Attachment], Field(max_length=10)] | None = None


class ScheduledMessageService:
    """Single responsible service for all scheduled-message concerns."""

    @staticmethod
    async def schedule(params: ScheduleMessageParams) -> None:
        """Schedule a new message to be sent at the given time."""

        from api import execute_action

        # Serialize attachments to JSON for storage
        attachments_json = None
        if params.attachments:
            attachments_json = json.dumps([att.model_dump() for att in params.attachments])

        query = """
        INSERT INTO scheduledMessages
        (guild_id, channel_id, user_id, content, send_time, repeatInterval, repeatAmount, attachments)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db_params = (
            params.guild_id,
            params.channel_id,
            params.user_id,
            params.content,
            params.send_time,
            params.repeat_interval,
            params.repeat_amount,
            attachments_json,
        )
        await execute_action(query, db_params)

    @staticmethod
    async def get_user_messages(user_id: UserId) -> list[ScheduledMessageModel]:
        """Return all scheduled messages for a given user, ordered by send_time."""

        query = """
        SELECT messageId, guild_id, channel_id, user_id, content, send_time,
               repeatInterval, repeatAmount, attachments, created_at
        FROM scheduledMessages
        WHERE user_id = %s
        ORDER BY send_time ASC
        """
        rows: list[ScheduledMessageModel] = []
        async for row in ScheduledMessageModel.iter_rows(query, (user_id,)):
            rows.append(row)
        return rows

    @staticmethod
    async def cancel(message_id: int) -> None:
        """Delete a scheduled message by its ID."""
        from api import execute_action

        query = "DELETE FROM scheduledMessages WHERE messageId = %s"
        await execute_action(query, (message_id,))

    @staticmethod
    async def update_content(message_id: int, content: str) -> None:
        """Update the content of a scheduled message."""
        from api import execute_action

        query = "UPDATE scheduledMessages SET content = %s WHERE messageId = %s"
        await execute_action(query, (content, message_id))

    @staticmethod
    async def update_repeat(message_id: int, repeat_amount: int) -> None:
        """Update the repeat amount of a scheduled message."""
        from api import execute_action

        query = "UPDATE scheduledMessages SET repeatAmount = %s WHERE messageId = %s"
        await execute_action(query, (repeat_amount, message_id))

    @staticmethod
    async def update_send_time(message_id: int, send_time: datetime) -> None:
        """Update the send time of a scheduled message (for repeat advancement)."""
        from api import execute_action

        query = "UPDATE scheduledMessages SET send_time = %s WHERE messageId = %s"
        await execute_action(query, (send_time, message_id))

    @staticmethod
    async def update_repeat_and_send_time(message_id: int, repeat_amount: int, send_time: datetime) -> None:
        """Atomically update both repeat amount and send time in a single query."""
        from api import execute_action

        query = "UPDATE scheduledMessages SET repeatAmount = %s, send_time = %s WHERE messageId = %s"
        await execute_action(query, (repeat_amount, send_time, message_id))

    @staticmethod
    async def get_due_messages() -> list[ScheduledMessageModel]:
        """Return all messages whose send_time is due (<= now)."""

        query = """
        SELECT messageId, guild_id, channel_id, user_id, content, send_time,
               repeatInterval, repeatAmount, attachments, created_at
        FROM scheduledMessages WHERE send_time <= NOW()
        """
        rows: list[ScheduledMessageModel] = []
        async for row in ScheduledMessageModel.iter_rows(query):
            rows.append(row)
        return rows

    @staticmethod
    async def get_upcoming(
        user_id: UserId,
        start_time: datetime,
        end_time: datetime,
        guild_id: GuildId | None = None,
    ) -> list[ScheduledMessageModel]:
        """Return messages scheduled within a time window for a user, optionally filtered by guild."""

        query = """
        SELECT messageId, guild_id, channel_id, user_id, content, send_time,
               repeatInterval, repeatAmount, attachments, created_at
        FROM scheduledMessages
        WHERE user_id = %s
        AND send_time BETWEEN %s AND %s
        """
        db_params: list[Any] = [user_id, start_time, end_time]

        if guild_id:
            query += " AND guild_id = %s"
            db_params.append(guild_id)

        rows: list[ScheduledMessageModel] = []
        async for row in ScheduledMessageModel.iter_rows(query, tuple(db_params)):
            rows.append(row)
        return rows
