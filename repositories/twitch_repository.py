"""TwitchRepository: Consolidated CRUD for Twitch online notifications."""

from __future__ import annotations

from dataclasses import dataclass

from models import TwitchOnlineNotificationModel


@dataclass
class TwitchRepository:
    """Repository for managing Twitch online notification subscriptions."""

    async def get_by_channel(self, channel_id: str) -> list[TwitchOnlineNotificationModel]:
        """Get all Twitch notifications for a Discord channel."""
        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE channel_id = %s"
        params = (channel_id,)
        rows: list[TwitchOnlineNotificationModel] = []
        async for row in TwitchOnlineNotificationModel.iter_rows(query, params):
            rows.append(row)
        return rows

    async def set(
        self,
        guild_id: str,
        channel_id: str,
        twitch_uuid: str,
        twitch_name: str,
        notification_message: str,
    ) -> None:
        """Create a Twitch online notification subscription."""
        from api import execute_action

        query = "INSERT INTO twitchOnlineNotification (guild_id, channel_id, twitchUuid, twitchName, notification_message) VALUES (%s, %s, %s, %s, %s)"
        params = (guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
        await execute_action(query, params)

    async def remove(self, id: str) -> None:
        """Remove a Twitch notification by ID."""
        from api import execute_action

        query = "DELETE FROM twitchOnlineNotification WHERE id = %s"
        params = (id,)
        await execute_action(query, params)

    async def get_by_twitch_uuid(self, twitch_uuid: str) -> TwitchOnlineNotificationModel | None:
        """Get a Twitch notification by Twitch user UUID."""
        from api import safe_execute_query

        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE twitchUuid = %s"
        params = (twitch_uuid,)
        result = await safe_execute_query(query, params)
        return TwitchOnlineNotificationModel.from_row(result[0]) if result else None

    async def get_all_uuids(self) -> list[str]:
        """Get all tracked Twitch user UUIDs."""
        from api import execute_query_iter

        query = "SELECT twitchUuid FROM twitchOnlineNotification"
        uuids: list[str] = []
        async for row in execute_query_iter(query):
            uuids.append(row[0])
        return uuids

    async def get_by_guild(self, guild_id: str) -> list[TwitchOnlineNotificationModel]:
        """Get all Twitch notifications for a guild."""
        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[TwitchOnlineNotificationModel] = []
        async for row in TwitchOnlineNotificationModel.iter_rows(query, params):
            rows.append(row)
        return rows


# Module-level singleton for easy import
twitch_repo = TwitchRepository()
