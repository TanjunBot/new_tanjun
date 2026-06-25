"""Twitch Service: Encapsulates Twitch notification CRUD and API client logic.

Consolidates the module-level Twitch API functions from api.py and twitch_api.py
into a single TwitchService class with typed Pydantic models.
"""
from __future__ import annotations

from locale_keys import locale as _locale
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
import aiohttp
import discord
from aiohttp import ClientTimeout
from api import execute_action, execute_query_iter, safe_execute_query
from config import twitchId, twitchSecret
from models import TwitchUserModel
from utility import tanjunEmbed

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
        return cls(user_id=data.get('user_id', ''), user_name=data.get('user_name', ''), title=data.get('title', ''), viewer_count=data.get('viewer_count', 0), started_at=data.get('started_at', ''), thumbnail_url=data.get('thumbnail_url', ''))

class TwitchService:
    """Consolidated service for Twitch API interaction and notification management."""

    def __init__(self) -> None:
        self.client_id = twitchId
        self.client_secret = twitchSecret
        self.access_token: str | None = None
        self.session: aiohttp.ClientSession | None = None
        self.headers: Mapping[str, str] | None = None
        self.base_url = 'https://api.twitch.tv/helix'
        self.stream_status: dict[str, bool] = {}
        self.initial_check_done = False

    async def init(self) -> None:
        """Initialize the Twitch API session and obtain an app access token."""
        self.session = aiohttp.ClientSession()
        await self._get_app_access_token()
        await self._setup_headers()

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_app_access_token(self) -> None:
        """Obtain an OAuth app access token from Twitch."""
        auth_url = 'https://id.twitch.tv/oauth2/token'
        if self.session is None or self.client_id is None or self.client_secret is None:
            return
        params: Mapping[str, str] = {'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'client_credentials'}
        try:
            async with self.session.post(url=auth_url, params=params, timeout=ClientTimeout(total=10)) as response:
                data = await response.json()
                self.access_token = data['access_token']
        except (TimeoutError, aiohttp.ClientError) as e:
            print(f'Error getting Twitch access token: {e}')
            self.access_token = None
        except Exception as e:
            print(f'Unexpected error getting Twitch access token: {e}')
            self.access_token = None

    async def _setup_headers(self) -> None:
        """Set up HTTP headers for Twitch API requests."""
        if self.client_id is None or self.client_secret is None or (not self.access_token):
            self.headers = None
            return
        self.headers = {'Client-ID': self.client_id, 'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

    async def get_user_by_login(self, login_name: str) -> TwitchUserModel | None:
        """Look up a Twitch user by their login name."""
        if self.session is None:
            return None
        url = f'{self.base_url}/users'
        params = {'login': login_name}
        async with self.session.get(url, headers=self.headers, params=params, timeout=ClientTimeout(total=10)) as response:
            data: dict[str, list[dict[str, str]]] = await response.json()
            if data['data']:
                return TwitchUserModel.from_api_response(data['data'][0])
            return None

    async def get_streams(self, user_ids: list[str]) -> list[LiveStreamInfo]:
        """Get live stream data for the given user IDs."""
        if not user_ids or self.session is None:
            return []
        url = f'{self.base_url}/streams'
        params = {'user_id': user_ids}
        try:
            async with self.session.get(url, headers=self.headers, params=params, timeout=ClientTimeout(total=10)) as response:
                data: dict[str, list[dict[str, Any]]] = await response.json()
                return [LiveStreamInfo.from_api_data(item) for item in data.get('data', [])]
        except (TimeoutError, aiohttp.ClientError):
            return []

    async def initialize_stream_status(self, user_ids: list[str]) -> None:
        """Populate initial stream status for all tracked users."""
        if not user_ids:
            return
        streams = await self.get_streams(user_ids)
        for uuid in user_ids:
            self.stream_status[uuid] = any((stream.user_id == uuid for stream in streams))
        self.initial_check_done = True

    async def get_notifications(self, channel_id: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for a given channel."""
        query = 'SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE channel_id = %s'
        params = (channel_id,)
        rows: list[TwitchNotification] = []
        async for row in execute_query_iter(query, params):
            rows.append(TwitchNotification(*row))
        return rows

    async def add_notification(self, guild_id: str, channel_id: str, twitch_uuid: str, twitch_name: str, notification_message: str | None=None) -> None:
        """Add a new Twitch live notification subscription."""
        query = 'INSERT INTO twitchOnlineNotification (guild_id, channel_id, twitchUuid, twitchName, notification_message) VALUES (%s, %s, %s, %s, %s)'
        params = (guild_id, channel_id, twitch_uuid, twitch_name, notification_message)
        await execute_action(query, params)

    async def remove_notification(self, notification_id: str) -> None:
        """Remove a Twitch live notification subscription by ID."""
        query = 'DELETE FROM twitchOnlineNotification WHERE id = %s'
        params = (notification_id,)
        await execute_action(query, params)

    async def get_notification_by_twitch_uuid(self, twitch_uuid: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for the given Twitch user UUID."""
        query = 'SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE twitchUuid = %s'
        params = (twitch_uuid,)
        result = await safe_execute_query(query, params)
        if result:
            return [TwitchNotification(*row) for row in result]
        return []

    async def get_all_notification_uuids(self) -> list[str]:
        """Get all unique Twitch UUIDs that have active notifications."""
        query = 'SELECT DISTINCT twitchUuid FROM twitchOnlineNotification'
        uuids: list[str] = []
        async for row in execute_query_iter(query):
            uuids.append(row[0])
        return uuids

    async def get_notifications_by_guild(self, guild_id: str) -> list[TwitchNotification]:
        """Get all Twitch notifications for a given guild."""
        query = 'SELECT id, channel_id, guild_id, twitchUuid, twitchName, notification_message FROM twitchOnlineNotification WHERE guild_id = %s'
        params = (guild_id,)
        rows: list[TwitchNotification] = []
        async for row in execute_query_iter(query, params):
            rows.append(TwitchNotification(*row))
        return rows

    async def send_live_notification(self, client: discord.Client, twitch_uuid: str, stream_data: LiveStreamInfo) -> None:
        """Send Twitch live notifications to all configured channels for this user."""
        notifications = await self.get_notification_by_twitch_uuid(twitch_uuid)
        if not notifications:
            return
        for notification in notifications:
            channel_id = notification.channel_id
            notification_message = notification.notification_message
            guild_id = notification.guild_id
            guild = client.get_guild(int(guild_id))
            if guild is None:
                continue
            message = self.parse_notification_message(notification_message, str(guild.preferred_locale), stream_data.user_name)
            channel = guild.get_channel(int(channel_id))
            if channel is None or isinstance(channel, (discord.ForumChannel, discord.CategoryChannel)):
                continue
            embed = tanjunEmbed(description=f"[{stream_data.title}](https://www.twitch.tv/{stream_data.user_name})")
            embed.set_image(url=stream_data.thumbnail_url.replace('{width}', '1920').replace('{height}', '1080'))
            await channel.send(message, embed=embed)

    def parse_notification_message(self, message: str | None, locale_str: str, twitch_name: str) -> str:
        """Parse a notification message template, replacing {name} with the Twitch user's name."""
        if not message:
            return _locale.commands.utility.twitch.defaultNotificationMessage(locale_str).replace('{name}', twitch_name)
        return message.replace('{name}', twitch_name)
_twitch_service: TwitchService | None = None

async def init_twitch_service() -> TwitchService:
    """Initialize and return the global TwitchService singleton."""
    global _twitch_service
    print('Initiating Twitch Service...')
    if _twitch_service is not None:
        await _twitch_service.close()
    _twitch_service = TwitchService()
    await _twitch_service.init()
    print('Twitch Service initiated!')
    return _twitch_service

def get_twitch_service() -> TwitchService | None:
    """Get the global TwitchService singleton."""
    return _twitch_service
