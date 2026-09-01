"""Twitch Service: Encapsulates Twitch notification CRUD and API client logic.

Consolidates the module-level Twitch API functions from api.py and twitch_api.py
into a single TwitchService class with typed Pydantic models.
"""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aiohttp
import discord
from aiohttp import ClientTimeout

from api import execute_action, execute_query_iter, safe_execute_query
from config import twitchId, twitchSecret
from locale_keys import locale as _locale
from models import TwitchUserModel
from utility import tanjunEmbed

logger = logging.getLogger(__name__)


@dataclass
class TwitchNotification:
    """Represents a Twitch live notification subscription."""
    id: str
    channel_id: str
    guild_id: str
    twitch_uuid: str
    twitch_name: str
    notification_message: str | None


@dataclass
class LiveStreamInfo:
    """Represents a live Twitch stream."""
    user_id: str
    user_name: str
    title: str
    viewer_count: int
    started_at: str
    thumbnail_url: str

    @classmethod
    def from_api_data(cls, data: dict[str, Any]) -> LiveStreamInfo:
        return cls(
            user_id=data.get("user_id", ""),
            user_name=data.get("user_name", ""),
            title=data.get("title", ""),
            viewer_count=data.get("viewer_count", 0),
            started_at=data.get("started_at", ""),
            thumbnail_url=data.get("thumbnail_url", ""),
        )


class TwitchService:
    """Consolidated service for Twitch API interaction and notification management."""

    def __init__(self) -> None:
        self.client_id = twitchId
        self.client_secret = twitchSecret
        self.access_token: str | None = None
        self.session: aiohttp.ClientSession | None = None
        self.headers: Mapping[str, str] | None = None
        self.base_url = "https://api.twitch.tv/helix"
        self.stream_status: dict[str, bool] = {}
        self.initial_check_done = False

    async def init(self) -> None:
        """Initialize the Twitch API session and obtain an app access token."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        await self._get_app_access_token()
        await self._setup_headers()

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure an active aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _get_app_access_token(self) -> None:
        """Obtain an OAuth app access token from Twitch."""
        auth_url = "https://id.twitch.tv/oauth2/token"
        if self.client_id is None or self.client_secret is None:
            return
        session = await self._ensure_session()
        params: Mapping[str, str] = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }
        try:
            async with session.post(url=auth_url, params=params, timeout=ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data.get("access_token")
                else:
                    logger.warning("Failed to obtain Twitch access token: HTTP %s", response.status)
                    self.access_token = None
        except (TimeoutError, aiohttp.ClientError) as e:
            logger.warning("Error getting Twitch access token: %s", e)
            self.access_token = None
        except Exception as e:
            logger.error("Unexpected error getting Twitch access token: %s", e)
            self.access_token = None

    async def _setup_headers(self) -> None:
        """Set up HTTP headers for Twitch API requests."""
        if self.client_id is None or self.client_secret is None or not self.access_token:
            self.headers = None
            return
        self.headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        url: str,
        params: Any = None,
        retry_auth: bool = True,
    ) -> tuple[int, dict[str, Any] | None]:
        """Perform an HTTP request with automatic token refresh on HTTP 401."""
        session = await self._ensure_session()
        if not self.headers or not self.access_token:
            await self._get_app_access_token()
            await self._setup_headers()

        try:
            async with session.request(
                method,
                url,
                headers=self.headers,
                params=params,
                timeout=ClientTimeout(total=10),
            ) as response:
                if response.status == 401 and retry_auth:
                    logger.info("Twitch API returned 401 Unauthorized; refreshing access token...")
                    await self._get_app_access_token()
                    await self._setup_headers()
                    return await self._request(method, url, params=params, retry_auth=False)

                try:
                    data = await response.json()
                except Exception:
                    data = None
                return response.status, data
        except (TimeoutError, aiohttp.ClientError) as e:
            logger.warning("Twitch API request error (%s %s): %s", method, url, e)
            return 0, None
        except Exception as e:
            logger.exception("Unexpected Twitch API request error (%s %s): %s", method, url, e)
            return 0, None

    async def get_user_by_login(self, login_name: str) -> TwitchUserModel | None:
        """Look up a Twitch user by their login name."""
        url = f"{self.base_url}/users"
        params = {"login": login_name}
        status, data = await self._request("GET", url, params=params)
        if status == 200 and data and isinstance(data.get("data"), list) and data["data"]:
            return TwitchUserModel.from_api_response(data["data"][0])
        return None

    async def get_streams(self, user_ids: list[str]) -> list[LiveStreamInfo] | None:
        """Get live stream data for the given user IDs in chunks of up to 100."""
        if not user_ids:
            return []

        url = f"{self.base_url}/streams"
        all_streams: list[LiveStreamInfo] = []
        any_success = False

        # Twitch Helix API allows at most 100 user_ids per query
        chunk_size = 100
        for i in range(0, len(user_ids), chunk_size):
            batch = user_ids[i : i + chunk_size]
            params = [("user_id", uid) for uid in batch]
            status, data = await self._request("GET", url, params=params)
            if status == 200 and data is not None and isinstance(data.get("data"), list):
                any_success = True
                all_streams.extend(LiveStreamInfo.from_api_data(item) for item in data.get("data", []))
            else:
                logger.warning("Twitch get_streams batch request returned HTTP status %s", status)

        if not any_success:
            return None

        return all_streams

    async def initialize_stream_status(self, user_ids: list[str]) -> None:
        """Populate initial stream status for all tracked users."""
        if not user_ids:
            return
        streams = await self.get_streams(user_ids)
        if streams is None:
            logger.warning("initialize_stream_status: initial streams fetch failed; will retry on next poll")
            return
        live_uuids = {stream.user_id for stream in streams}
        for uuid in user_ids:
            self.stream_status[uuid] = uuid in live_uuids
        self.initial_check_done = True

    async def get_notifications(self, channel_id: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for a given channel."""
        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE channel_id = %s"
        params = (channel_id,)
        rows: list[TwitchNotification] = []
        async for row in execute_query_iter(query, params):
            rows.append(TwitchNotification(*row))
        return rows

    async def add_notification(
        self,
        guild_id: str,
        channel_id: str,
        twitch_uuid: str,
        twitch_name: str,
        notification_message: str | None = None,
    ) -> None:
        """Add a new Twitch live notification subscription."""
        query = "INSERT INTO twitchOnlineNotification (guild_id, channel_id, twitchUuid, twitchName, notification_message) VALUES (%s, %s, %s, %s, %s)"
        params = (guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
        await execute_action(query, params)

    async def remove_notification(self, notification_id: str) -> None:
        """Remove a Twitch live notification subscription by ID."""
        query = "DELETE FROM twitchOnlineNotification WHERE id = %s"
        params = (notification_id,)
        await execute_action(query, params)

    async def get_notification_by_twitch_uuid(self, twitch_uuid: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for the given Twitch user UUID."""
        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE twitchUuid = %s"
        params = (twitch_uuid,)
        result = await safe_execute_query(query, params)
        if result:
            return [TwitchNotification(*row) for row in result]
        return []

    async def get_all_notification_uuids(self) -> list[str]:
        """Get all unique Twitch UUIDs that have active notifications."""
        query = "SELECT DISTINCT twitchUuid FROM twitchOnlineNotification"
        uuids: list[str] = []
        async for row in execute_query_iter(query):
            uuids.append(row[0])
        return uuids

    async def get_notifications_by_guild(self, guild_id: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for a given guild."""
        query = "SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE guild_id = %s"
        params = (guild_id,)
        rows: list[TwitchNotification] = []
        async for row in execute_query_iter(query, params):
            rows.append(TwitchNotification(*row))
        return rows

    async def send_live_notification(
        self, client: discord.Client, twitch_uuid: str, stream_data: LiveStreamInfo
    ) -> None:
        """Send Twitch live notifications to all configured channels for this user."""
        notifications = await self.get_notification_by_twitch_uuid(twitch_uuid)
        if not notifications:
            return
        for notification in notifications:
            try:
                channel_id = notification.channel_id
                notification_message = notification.notification_message
                guild_id = notification.guild_id
                guild = client.get_guild(int(guild_id))
                if guild is None:
                    continue
                message = self.parse_notification_message(
                    notification_message, str(guild.preferred_locale), stream_data.user_name
                )
                channel = guild.get_channel(int(channel_id))
                if channel is None:
                    channel = client.get_channel(int(channel_id))
                if channel is None and hasattr(guild, "get_thread"):
                    channel = guild.get_thread(int(channel_id))
                if channel is None:
                    try:
                        channel = await client.fetch_channel(int(channel_id))
                    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                        continue

                if channel is None or not hasattr(channel, "send") or isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
                    continue

                embed = tanjunEmbed(description=f"[{stream_data.title}](https://www.twitch.tv/{stream_data.user_name})")
                embed.set_image(url=stream_data.thumbnail_url.replace("{width}", "1920").replace("{height}", "1080"))
                await channel.send(message, embed=embed)
            except (discord.Forbidden, discord.NotFound, discord.HTTPException) as e:
                logger.warning("Failed to send Twitch live notification to channel %s: %s", notification.channel_id, e)
            except Exception:
                logger.exception("Unexpected error sending Twitch live notification for %s", twitch_uuid)

    def parse_notification_message(self, message: str | None, locale_str: str, twitch_name: str) -> str:
        """Parse a notification message template, replacing {name} with the Twitch user's name."""
        if not message:
            return _locale.commands.utility.twitch.defaultNotificationMessage(locale_str).replace("{name}", twitch_name)
        return message.replace("{name}", twitch_name)


_twitch_service: TwitchService | None = None


async def init_twitch_service() -> TwitchService:
    """Initialize and return the global TwitchService singleton."""
    global _twitch_service
    logger.info("Initiating Twitch Service...")
    if _twitch_service is not None:
        await _twitch_service.close()
    _twitch_service = TwitchService()
    await _twitch_service.init()
    logger.info("Twitch Service initiated!")
    return _twitch_service


def get_twitch_service() -> TwitchService | None:
    """Get the global TwitchService singleton."""
    return _twitch_service
