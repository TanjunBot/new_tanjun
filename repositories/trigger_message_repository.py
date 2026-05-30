"""TriggerMessageRepository: Consolidated CRUD for trigger message management."""

from __future__ import annotations

from dataclasses import dataclass

from models import TriggerMessageChannelModel, TriggerMessageModel


@dataclass
class TriggerMessageRepository:
    """Repository for managing trigger messages and their channel bindings."""

    async def get_all(self, guild_id: str) -> list[TriggerMessageModel]:
        """Get all trigger messages for a guild."""
        query = "SELECT id, guild_id, `trigger`, response, case_sensitive FROM triggerMessages WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[TriggerMessageModel] = []
        async for row in TriggerMessageModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def add(self, guild_id: str, trigger: str, response: str, case_sensitive: bool = False) -> None:
        """Add a trigger message."""
        from api import execute_action

        query = "INSERT INTO triggerMessages (guild_id, `trigger`, response, case_sensitive) VALUES (%s, %s, %s, %s)"
        params = (guild_id, trigger, response, case_sensitive)
        await execute_action(query, params)

    async def remove(self, guild_id: str, trigger: str) -> None:
        """Remove a trigger message by trigger string."""
        from api import execute_action

        query = "DELETE FROM triggerMessages WHERE guild_id = %s AND `trigger` = %s"
        params = (guild_id, trigger)
        await execute_action(query, params)

    async def get_channels(self, guild_id: str, trigger_id: int) -> list[TriggerMessageChannelModel]:
        """Get all channel bindings for a specific trigger."""
        query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND triggerId = %s"
        params = (guild_id, trigger_id)
        rows: list[TriggerMessageChannelModel] = []
        async for row in TriggerMessageChannelModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def get_by_channel(self, guild_id: str, channel_id: str) -> list[TriggerMessageChannelModel]:
        """Get all trigger-channel bindings for a specific channel."""
        query = "SELECT guild_id, channel_id, triggerId FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s"
        params = (guild_id, channel_id)
        rows: list[TriggerMessageChannelModel] = []
        async for row in TriggerMessageChannelModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def add_channel(self, guild_id: str, channel_id: str, trigger_id: int) -> None:
        """Bind a channel to a trigger message."""
        from api import execute_action

        query = "INSERT INTO triggerMessagesChannel (guild_id, channel_id, triggerId) VALUES (%s, %s, %s)"
        params = (guild_id, channel_id, trigger_id)
        await execute_action(query, params)

    async def remove_channel(self, guild_id: str, channel_id: str, trigger_id: int) -> None:
        """Unbind a channel from a trigger message."""
        from api import execute_action

        query = "DELETE FROM triggerMessagesChannel WHERE guild_id = %s AND channel_id = %s AND triggerId = %s"
        params = (guild_id, channel_id, trigger_id)
        await execute_action(query, params)

    async def find(self, guild_id: str, trigger: str, channel_id: str) -> TriggerMessageModel | None:
        """Find a trigger message that matches a given trigger and channel."""
        from api import execute_query

        query = """
            SELECT t.id, t.guild_id, t.`trigger`, t.response, t.case_sensitive FROM triggerMessages t
            LEFT JOIN triggerMessagesChannel tc ON t.id = tc.triggerId AND t.guild_id = tc.guild_id
            WHERE t.guild_id = %s AND t.`trigger` LIKE %s
            AND (tc.channel_id = %s)
        """
        params = (guild_id, trigger, channel_id)
        rows_result: list[tuple[Any, ...]] | None = await execute_query(query, params)
        row: tuple[Any, ...] | None = rows_result[0] if rows_result and rows_result[0] else None
        if not row:
            return None
        trigger_message = TriggerMessageModel.from_row(row)
        if trigger_message.case_sensitive:
            if trigger != trigger_message.trigger:
                return None
        else:
            if trigger.lower() != trigger_message.trigger.lower():
                return None
        return trigger_message


# Module-level singleton for easy import
trigger_message_repo = TriggerMessageRepository()
