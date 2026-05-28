"""AFK Service: Encapsulates AFK CRUD and auto-cleanup logic."""

from __future__ import annotations

from dataclasses import dataclass

from api import execute_action, execute_query_iter, safe_execute_query


@dataclass
class AfkEntry:
    """Represents a user's AFK status entry."""

    user_id: str
    reason: str | None = None
    # created_at is stored in the DB but not loaded here for simplicity


@dataclass
class AfkMessage:
    """Represents a message mentioning an AFK user (for auto-removal)."""

    message_id: str
    channel_id: str


class AfkService:
    """Consolidated service for AFK CRUD operations and auto-cleanup."""

    async def set_afk(self, user_id: str, reason: str | None = None) -> None:
        """Set a user's AFK status."""
        query = """
        INSERT INTO afk_users (user_id, reason)
        VALUES (%s, %s)
        """
        await execute_action(query, (user_id, reason))

    async def remove_afk(self, user_id: str) -> None:
        """Remove a user's AFK status and associated mention messages."""
        query = "DELETE FROM afk_users WHERE user_id = %s"
        await execute_action(query, (user_id,))
        query = "DELETE FROM afkMessages WHERE user_id = %s"
        await execute_action(query, (user_id,))

    async def is_afk(self, user_id: str) -> bool:
        """Check if a user is currently AFK."""
        query = "SELECT 1 FROM afk_users WHERE user_id = %s"
        result = await safe_execute_query(query, (user_id,))
        return result is not None and len(result) > 0

    async def get_reason(self, user_id: str) -> str | None:
        """Get the AFK reason for a user."""
        query = "SELECT reason FROM afk_users WHERE user_id = %s"
        result = await execute_query(query, (user_id,))
        return result[0][0] if result else None

    async def track_mention(self, user_id: str, message_id: str, channel_id: str) -> None:
        """Track a mention message for a user's AFK auto-removal."""
        query = """
        INSERT INTO afkMessages (user_id, messageId, channel_id)
        VALUES (%s, %s, %s)
        """
        await execute_action(query, (user_id, message_id, channel_id))

    async def get_mentions(self, user_id: str) -> list[AfkMessage]:
        """Get all tracked mention messages for a user."""
        query = "SELECT messageId, channel_id FROM afkMessages WHERE user_id = %s"
        rows: list[AfkMessage] = []
        async for message_id, channel_id in execute_query_iter(query, (user_id,)):
            rows.append(AfkMessage(message_id=message_id, channel_id=channel_id))
        return rows

    async def clear_and_notify(self, user_id: str) -> list[AfkMessage]:
        """Combined operation: get mentions, remove AFK, return mentions for notification."""
        mentions = await self.get_mentions(user_id)
        await self.remove_afk(user_id)
        return mentions


# Singleton instance for easy import
afk_service = AfkService()
