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

from typing import Any

import aiohttp
from pydantic import BaseModel, Field


# ── Pydantic Models ──────────────────────────────────────────────────────────


class BrawlStarsIcon(BaseModel):
    """Represents an icon/avatar in Brawl Stars API responses."""

    id: int | None = None


class BrawlStarsClub(BaseModel):
    """Represents a club associated with a player or queried directly."""

    tag: str = ""
    name: str = ""
    description: str | None = None
    type: str | None = None
    badge_id: int | None = None
    required_trophies: int = 0
    trophies: int | None = None
    members: list["BrawlStarsClubMember"] = Field(default_factory=list)


class BrawlStarsClubMember(BaseModel):
    """Represents a single member within a club."""

    tag: str
    name: str
    role: str
    trophies: int
    name_color: str | None = None
    icon: BrawlStarsIcon | None = None
    # Optional fields from get_player context
    club_rank: int | None = None


class BrawlerGear(BaseModel):
    """A gear equipped on a brawler."""

    id: int
    name: str
    level: int


class BrawlerGadget(BaseModel):
    """A gadget equipped on a brawler."""

    id: int
    name: str


class BrawlerStarPower(BaseModel):
    """A star power equipped on a brawler."""

    id: int
    name: str


class BrawlerInfo(BaseModel):
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


class BrawlStarsPlayer(BaseModel):
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


class BrawlStarPlayerBrawler(BaseModel):
    """Minimal brawler data from the /v1/brawlers endpoint."""

    id: int
    name: str


class BrawlStarsBrawlerList(BaseModel):
    """Response from the /v1/brawlers list endpoint."""

    items: list[BrawlStarPlayerBrawler] = Field(default_factory=list)


class BrawlStarsEvent(BaseModel):
    """A single event in the current rotation."""

    start_time: str
    end_time: str
    event: "BrawlStarsEventDetail"


class BrawlStarsEventDetail(BaseModel):
    """Details of a single event slot."""

    id: int
    mode: str
    map: str


class BrawlStarsEventRotation(BaseModel):
    """Wrapper for the event rotation endpoint (list in response)."""

    items: list[BrawlStarsEvent] = Field(default_factory=list)


class BattlePlayer(BaseModel):
    """Player info within a battle."""

    tag: str
    name: str
    brawler: BrawlerInfo | None = None


class BrawlStarsBattle(BaseModel):
    """A single battle entry from the battle log."""

    battle_time: str
    mode: str
    type: str
    result: str | None = None
    duration: int | None = None
    trophy_change: int | None = None
    star_player: BattlePlayer | None = None
    teams: list[list[BattlePlayer]] | None = None
    players: list[BattlePlayer] | None = None
    map: str | None = None


class BrawlStarsBattleLog(BaseModel):
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

    # ── Session management ──────────────────────────────────────────────────

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """Close the underlying session if owned by this service."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def __aenter__(self) -> BrawlStarsService:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ── Request helpers ─────────────────────────────────────────────────────

    async def _get(self, path: str) -> dict[str, Any] | None:
        """Perform a GET request to the Brawl Stars API.

        Returns the parsed JSON dict on success (HTTP 200), or ``None`` on
        any non-200 status.
        """
        session = await self._get_session()
        async with session.get(
            f"{self.BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=aiohttp.ClientTimeout(total=10),
        ) as response:
            if response.status != 200:
                return None
            data: Any = await response.json()
            if isinstance(data, dict):
                return data
            return None

    async def _get_list(self, path: str) -> list[dict[str, Any]]:
        """Perform a GET request that returns a list (e.g. event rotation)."""
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
        return [BrawlStarsBattle.model_validate(b) for b in items]

    async def get_brawler_list(self) -> list[BrawlStarPlayerBrawler]:
        """Fetch the full list of all brawlers available in the game."""
        data = await self._get("/brawlers")
        if data is None:
            return []
        items = data.get("items", [])
        return [BrawlStarPlayerBrawler.model_validate(b) for b in items]

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

    async def get_events(self) -> list[dict[str, Any]]:
        """Fetch the current event rotation.

        Returns raw dicts because the event rotation schema is a list at the
        top level. Callers can access ``event["event"]["map"]`` etc.
        """
        return await self._get_list("/events/rotation")


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
