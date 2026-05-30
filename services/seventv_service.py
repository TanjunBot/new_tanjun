"""7TV Service: Fetch emote data from the 7TV API v3.

Provides typed models and async methods to look up a user's 7TV emote set
by their Twitch username and retrieve emote details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

SEVENTV_API_BASE = "https://7tv.io/v3"
SEVENTV_CDN_BASE = "https://cdn.7tv.app"


@dataclass
class SevenTVEmote:
    """Represents a single emote from 7TV."""

    id: str
    name: str
    animated: bool
    owner_name: str | None
    tags: list[str] = field(default_factory=list)
    image_url: str = ""

    @classmethod
    def from_api_data(cls, data: dict[str, Any], active: dict[str, Any]) -> SevenTVEmote:
        """Construct an emote from the active emote data and its full data payload."""
        emote_data = active.get("data") or data
        emote_name = active.get("name", "unknown")
        emote_id = emote_data.get("id", "")
        animated = emote_data.get("animated", False)
        owner = emote_data.get("owner", {})
        owner_name = owner.get("display_name") or owner.get("username") if owner else None
        tags = emote_data.get("tags") or []

        # Build the image URL using the CDN host info
        host = emote_data.get("host", {})
        cdn_url = host.get("url", "")
        if cdn_url:
            files = host.get("files", [])
            # Find the 4x PNG (static) or 4x GIF (animated)
            ext = "gif" if animated else "png"
            for file in files:
                if file.get("name") == f"4x.{ext}":
                    image_url = f"https:{cdn_url}/4x.{ext}"
                    break
            else:
                # Fallback to 4x.webp
                image_url = f"https:{cdn_url}/4x.webp"
        else:
            image_url = f"{SEVENTV_CDN_BASE}/emote/{emote_id}/4x.png"

        return cls(
            id=emote_id,
            name=emote_name,
            animated=animated,
            owner_name=owner_name,
            tags=tags,
            image_url=image_url,
        )


@dataclass
class SevenTVUser:
    """Represents a 7TV user with their emote set."""

    id: str
    username: str
    display_name: str
    avatar_url: str
    emote_set_id: str | None
    emotes: list[SevenTVEmote] = field(default_factory=list)


class SevenTVService:
    """Service for interacting with the 7TV API."""

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_user_by_twitch(self, twitch_username: str) -> SevenTVUser | None:
        """Look up a 7TV user by their Twitch username using the platform endpoint."""
        session = await self._get_session()
        try:
            # Twitch connection IDs on 7TV are Twitch user IDs (numeric), not usernames.
            # First try to search via the GraphQL endpoint
            return await self._search_user_by_twitch_name(session, twitch_username)
        except Exception:
            return None

    async def _search_user_by_twitch_name(self, session: aiohttp.ClientSession, twitch_username: str) -> SevenTVUser | None:
        """Search for a user by their Twitch connection name via GraphQL."""
        query = """
        query SearchUsers($query: String!) {
            users(query: $query, limit: 5) {
                id
                username
                display_name
                avatar_url
                connections {
                    id
                    platform
                    username
                    emote_set_id
                }
            }
        }
        """
        response = await session.post(
            f"{SEVENTV_API_BASE}/gql",
            json={"query": query, "variables": {"query": twitch_username}},
            timeout=ClientTimeout(total=15),
        )
        if response.status != 200:
            return None

        data = await response.json()
        try:
            users_data = data.get("data", {}).get("users", [])
        except (KeyError, TypeError, AttributeError):
            return None

        # Find the matching user with a Twitch connection
        for user_data in users_data:
            connections = user_data.get("connections", [])
            for conn in connections:
                if conn.get("platform") == "TWITCH" and conn.get("username", "").lower() == twitch_username.lower():
                    emote_set_id = conn.get("emote_set_id")
                    user = SevenTVUser(
                        id=user_data.get("id", ""),
                        username=user_data.get("username", ""),
                        display_name=user_data.get("display_name", ""),
                        avatar_url=user_data.get("avatar_url", ""),
                        emote_set_id=emote_set_id,
                    )
                    if emote_set_id:
                        await self._populate_emotes(session, user, emote_set_id)
                    return user

        return None

    async def _populate_emotes(self, session: aiohttp.ClientSession, user: SevenTVUser, emote_set_id: str) -> None:
        """Fetch all emotes for the given emote set ID and populate the user object."""
        try:
            response = await session.get(
                f"{SEVENTV_API_BASE}/emote-sets/{emote_set_id}",
                timeout=ClientTimeout(total=15),
            )
            if response.status != 200:
                return

            data = await response.json()
            emote_set = data.get("emote_set", data)  # Handle potential wrapping
            emotes_data = emote_set.get("emotes", []) if isinstance(emote_set, dict) else []

            for active_emote in emotes_data:
                emote = SevenTVEmote.from_api_data(active_emote.get("data", {}), active_emote)
                user.emotes.append(emote)

        except Exception:
            return

    async def get_emote_image_bytes(self, image_url: str) -> bytes | None:
        """Download the raw image data for a 7TV emote."""
        session = await self._get_session()
        try:
            async with session.get(image_url, timeout=ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.read()
        except Exception:
            return None
        return None


# Module-level singleton
_seventv_service: SevenTVService | None = None


def get_seventv_service() -> SevenTVService:
    """Get or create the singleton SevenTVService instance."""
    global _seventv_service
    if _seventv_service is None:
        _seventv_service = SevenTVService()
    return _seventv_service
