"""
BrawlStarsService: Typed client for the Brawl Stars API with Pydantic response models.

Consolidates all raw API calls scattered across commands/utility/brawlstars/* into a single
service with proper response validation, centralized rate-limit handling, and shared session
management.

Usage:
    from services.brawlstars import BrawlStarsService

    service = BrawlStarsService()
    player = await service.get_player("#ABC123")
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from typing import Any

import aiohttp
from pydantic import AliasPath, BaseModel, ConfigDict, Field, TypeAdapter

logger = logging.getLogger(__name__)

# ── Pydantic Models ──────────────────────────────────────────────────────────


def to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class BrawlStarsBaseModel(BaseModel):
    """Base model with camelCase alias support for all Brawl Stars models."""

    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
    )


class BrawlStarsIcon(BrawlStarsBaseModel):
    """Represents an icon/avatar in Brawl Stars API responses."""

    id: int | None = None


class BrawlStarsClubMember(BrawlStarsBaseModel):
    """Represents a single member within a club."""

    tag: str
    name: str
    role: str
    trophies: int
    name_color: str | None = None
    icon: BrawlStarsIcon | None = None
    # Optional fields from get_player context
    club_rank: int | None = None


class BrawlStarsClub(BrawlStarsBaseModel):
    """Represents a club associated with a player or queried directly."""

    tag: str = ""
    name: str = ""
    description: str | None = None
    type: str | None = None
    badge_id: int | None = None
    required_trophies: int = 0
    trophies: int | None = None
    members: list[BrawlStarsClubMember] = Field(default_factory=list)


class BrawlerGear(BrawlStarsBaseModel):
    """A gear equipped on a brawler."""

    id: int
    name: str
    level: int


class BrawlerGadget(BrawlStarsBaseModel):
    """A gadget equipped on a brawler."""

    id: int
    name: str


class BrawlerStarPower(BrawlStarsBaseModel):
    """A star power equipped on a brawler."""

    id: int
    name: str


class BrawlerInfo(BrawlStarsBaseModel):
    """Detailed info for a single brawler a player owns."""

    id: int
    name: str
    power: int
    rank: int
    trophies: int
    highest_trophies: int
    gears: list[BrawlerGear] = Field(default_factory=list)
    gadgets: list[BrawlerGadget] = Field(default_factory=list)
    star_powers: list[BrawlerStarPower] = Field(default_factory=list)


class BattleBrawler(BrawlStarsBaseModel):
    """Minimal brawler data from battle log payloads."""

    id: int
    name: str
    power: int
    trophies: int


class BrawlStarsPlayer(BrawlStarsBaseModel):
    """Full player model returned by the Brawl Stars API."""

    tag: str
    name: str
    trophies: int = 0
    highest_trophies: int = 0
    exp_level: int = 0
    exp_points: int = 0
    is_qualified_from_championship: bool = False
    duo_wins: int = 0
    solo_wins: int = 0
    x3vs3_victories: int = 0
    solo_victories: int = 0
    duo_victories: int = 0
    club: BrawlStarsClub | None = None
    brawlers: list[BrawlerInfo] = Field(default_factory=list)
    name_color: str | None = None
    icon: BrawlStarsIcon | None = None


class BrawlStarPlayerBrawler(BrawlStarsBaseModel):
    """Minimal brawler data from the /v1/brawlers endpoint."""

    id: int
    name: str


class BrawlStarsBrawlerList(BrawlStarsBaseModel):
    """Response from the /v1/brawlers list endpoint."""

    items: list[BrawlStarPlayerBrawler] = Field(default_factory=list)


class BrawlStarsEventDetail(BrawlStarsBaseModel):
    """Details of a single event slot."""

    id: int
    mode: str
    map: str


class BrawlStarsEvent(BrawlStarsBaseModel):
    """A single event in the current rotation."""

    start_time: str
    end_time: str
    event: BrawlStarsEventDetail


class BrawlStarsEventRotation(BrawlStarsBaseModel):
    """Wrapper for the event rotation endpoint (list in response)."""

    items: list[BrawlStarsEvent] = Field(default_factory=list)


class BattlePlayer(BrawlStarsBaseModel):
    """Player info within a battle."""

    tag: str
    name: str
    brawler: BattleBrawler | None = None


class BrawlStarsBattle(BrawlStarsBaseModel):
    """A single battle entry from the battle log."""

    battle_time: str = Field(validation_alias="battleTime")
    mode: str = Field(validation_alias=AliasPath("event", "mode"))
    type: str = Field(validation_alias=AliasPath("battle", "type"))
    result: str | None = Field(default=None, validation_alias=AliasPath("battle", "result"))
    duration: int | None = Field(default=None, validation_alias=AliasPath("battle", "duration"))
    trophy_change: int | None = Field(default=None, validation_alias=AliasPath("battle", "trophyChange"))
    star_player: BattlePlayer | None = Field(default=None, validation_alias=AliasPath("battle", "starPlayer"))
    teams: list[list[BattlePlayer]] | None = Field(default=None, validation_alias=AliasPath("battle", "teams"))
    players: list[BattlePlayer] | None = Field(default=None, validation_alias=AliasPath("battle", "players"))
    map: str | None = Field(default=None, validation_alias=AliasPath("event", "map"))


class BrawlStarsBattleLog(BrawlStarsBaseModel):
    """Response from the battle log endpoint."""

    items: list[BrawlStarsBattle] = Field(default_factory=list)


# ── Service ──────────────────────────────────────────────────────────────────


class BrawlStarsService:
    """Typed HTTP client for the Brawl Stars API.

    Manages a reusable aiohttp.ClientSession, reads the API token from
    environment (``brawlstarsToken``), and returns Pydantic-validated models
    instead of raw dicts.
    """

    BASE_URL = "https://api.brawlstars.com/v1"

    def __init__(self, token: str | None = None, session: aiohttp.ClientSession | None = None) -> None:
        """Initialise with an optional token and optional shared session.

        When ``session`` is ``None`` a new one will be created on first request
        and reused for the lifetime of the service.
        """
        from config import brawlstarsToken  # noqa: PLC0415

        self._token: str = token or brawlstarsToken
        self._session: aiohttp.ClientSession | None = session
        self._owns_session: bool = session is None

    # ── Session management ──────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Close the underlying session if owned by this service."""
        if self._session is not None and not self._session.closed and self._owns_session:
            await self._session.close()

    async def __aenter__(self) -> BrawlStarsService:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ── Request helpers ─────────────────────────────────────────────────────

    async def _get(self, path: str, max_retries: int = 3) -> dict[str, Any] | None:
        """Perform a GET request to the Brawl Stars API with retry logic.

        Implements exponential backoff with jitter for rate limits (HTTP 429)
        and server errors (HTTP 503). Returns the parsed JSON dict on success
        (HTTP 200), or ``None`` on persistent errors.
        """
        try:
            session = await self._get_session()
            for attempt in range(max_retries + 1):
                async with session.get(
                    f"{self.BASE_URL}{path}",
                    headers={"Authorization": f"Bearer {self._token}"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        data: Any = await response.json()
                        if isinstance(data, dict):
                            return data
                        return None

                    if response.status in (429, 503) and attempt < max_retries:
                        retry_after = response.headers.get("Retry-After")
                        if retry_after and retry_after.isdigit():
                            delay = float(retry_after)
                        else:
                            delay = (2**attempt) * random.uniform(0.5, 1.5)
                        logger.warning(
                            "Rate limit/server error on %s (attempt %d/%d): HTTP %d. Retrying in %.2fs",
                            path,
                            attempt + 1,
                            max_retries + 1,
                            response.status,
                            delay,
                        )
                        await asyncio.sleep(delay)
                        continue

                    return None
        except (TimeoutError, aiohttp.ClientError, json.JSONDecodeError, ValueError):
            return None
        return None

    async def _get_list(self, path: str) -> list[dict[str, Any]]:
        """Perform a GET request that returns a list (e.g. event rotation).

        Returns an empty list on network errors, timeouts, or JSON parsing errors.
        """
        try:
            session = await self._get_session()
            async with session.get(
                f"{self.BASE_URL}{path}",
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    return []
                data: Any = await response.json()
                if isinstance(data, list):
                    return data
                return []
        except (TimeoutError, aiohttp.ClientError, json.JSONDecodeError, ValueError):
            return []

    # ── Player endpoints ────────────────────────────────────────────────────

    async def get_player(self, tag: str) -> BrawlStarsPlayer | None:
        """Fetch full player info from the Brawl Stars API.

        The tag should include the ``#`` prefix (e.g. ``#ABC123``).
        """
        data = await self._get(f"/players/%23{tag[1:]}")
        if data is None:
            return None
        return BrawlStarsPlayer.model_validate(data)

    async def get_battle_log(self, tag: str) -> list[BrawlStarsBattle]:
        """Fetch the recent battle log for a player."""
        data = await self._get(f"/players/%23{tag[1:]}/battlelog")
        if data is None:
            return []
        items = data.get("items", [])
        battle_adapter = TypeAdapter(list[BrawlStarsBattle])
        return battle_adapter.validate_python(items)

    async def get_brawler_list(self) -> list[BrawlStarPlayerBrawler]:
        """Fetch the full list of all brawlers available in the game."""
        data = await self._get("/brawlers")
        if data is None:
            return []
        items = data.get("items", [])
        brawler_adapter = TypeAdapter(list[BrawlStarPlayerBrawler])
        return brawler_adapter.validate_python(items)

    # ── Club endpoints ──────────────────────────────────────────────────────

    async def get_club(self, tag: str) -> BrawlStarsClub | None:
        """Fetch club information.

        The tag should include the ``#`` prefix (e.g. ``#ABC123``).
        """
        data = await self._get(f"/clubs/%23{tag[1:]}")
        if data is None:
            return None
        return BrawlStarsClub.model_validate(data)

    # ── Events endpoints ────────────────────────────────────────────────────

    async def get_events(self) -> list[BrawlStarsEvent]:
        """Fetch the current event rotation.

        Returns parsed BrawlStarsEvent model instances.
        """
        data = await self._get_list("/events/rotation")
        event_adapter = TypeAdapter(list[BrawlStarsEvent])
        return event_adapter.validate_python(data)

    # ── Account linking helpers (database-backed) ───────────────────────────

    async def get_linked_account(self, user_id: str) -> str | None:
        """Get the Brawl Stars tag linked to a Discord user."""
        from api import get_brawlstars_linked_account  # noqa: PLC0415

        return await get_brawlstars_linked_account(user_id)

    async def link_account(self, user_id: str, brawlstars_tag: str) -> None:
        """Link a Brawl Stars tag to a Discord user."""
        from api import add_brawlstars_linked_account  # noqa: PLC0415

        await add_brawlstars_linked_account(user_id, brawlstars_tag)

    async def unlink_account(self, user_id: str) -> None:
        """Remove the Brawl Stars link for a Discord user."""
        from api import remove_brawlstars_linked_account  # noqa: PLC0415

        await remove_brawlstars_linked_account(user_id)


# Module-level singleton for convenient import
_default_service: BrawlStarsService | None = None


def get_brawlstars_service() -> BrawlStarsService:
    """Return the application-wide BrawlStarsService singleton.

    Creates it on first call.
    """
    global _default_service  # noqa: PLW0603
    if _default_service is None:
        _default_service = BrawlStarsService()
    return _default_service
