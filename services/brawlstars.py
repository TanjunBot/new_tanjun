"""
BrawlStarsService: Typed client for Brawl Stars API with Pydantic response models.

Consolidates raw API calls across commands/utility/brawlstars/* into a single
service class with validated Pydantic models. Reuses one aiohttp session and
centralizes rate-limit handling with retry logic and exponential backoff.
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from pydantic import BaseModel, Field

from config import brawlstarsToken

logger = logging.getLogger(__name__)

# ---- Pydantic response models ----


class BrawlStarsClub(BaseModel):
    """A club the player belongs to."""

    tag: str = ""
    name: str = ""


class BrawlerGear(BaseModel):
    """A single gear item on a brawler."""

    id: int = 0
    name: str = ""
    level: int = 1


class BrawlerGadget(BaseModel):
    """A single gadget on a brawler."""

    id: int = 0
    name: str = ""


class BrawlerStarPower(BaseModel):
    """A single star power on a brawler."""

    id: int = 0
    name: str = ""


class BrawlerInfo(BaseModel):
    """A brawler on a player's roster."""

    id: int = 0
    name: str = ""
    power: int = 1
    rank: int = 1
    trophies: int = 0
    highest_trophies: int = 0
    gears: list[BrawlerGear] = Field(default_factory=list)
    gadgets: list[BrawlerGadget] = Field(default_factory=list)
    star_powers: list[BrawlerStarPower] = Field(default_factory=list)


class BrawlStarsPlayer(BaseModel):
    """A Brawl Stars player profile."""

    tag: str = ""
    name: str = ""
    name_color: str = ""
    trophies: int = 0
    highest_trophies: int = 0
    exp_level: int = 0
    exp_points: int = 0
    is_qualified_from_championship: bool = False
    solo_victories: int = 0
    duo_victories: int = 0
    x3vs3_victories: int = 0
    club: BrawlStarsClub | None = None
    brawlers: list[BrawlerInfo] = Field(default_factory=list)


class BattleBrawler(BaseModel):
    """A brawler used in a battle."""

    name: str = ""
    power: int = 1
    trophies: int = 0


class BattlePlayer(BaseModel):
    """A player in a battle."""

    tag: str = ""
    name: str = ""
    brawler: BattleBrawler = Field(default_factory=BattleBrawler)


class BattleEvent(BaseModel):
    """The event (map + mode) a battle was played on."""

    mode: str = ""
    map: str = ""
    id: int = 0


class BattleResult(BaseModel):
    """Details of a single battle from the battle log."""

    mode: str = ""
    type: str = ""
    result: str = ""
    duration: int | None = None
    trophy_change: int | None = None
    brawler: BattleBrawler | None = None
    map: str | None = None
    star_player: BattlePlayer | None = None
    players: list[BattlePlayer] = Field(default_factory=list)
    teams: list[list[BattlePlayer]] = Field(default_factory=list)


class BattleLogItem(BaseModel):
    """A single entry in a player's battle log."""

    battle_time: str = ""
    event: BattleEvent = Field(default_factory=BattleEvent)
    battle: BattleResult = Field(default_factory=BattleResult)


class BrawlStarsClubMember(BaseModel):
    """A member of a club."""

    tag: str = ""
    name: str = ""
    trophies: int = 0
    role: str = "member"


class BrawlStarsClubFull(BaseModel):
    """A full club profile with members."""

    tag: str = ""
    name: str = ""
    description: str = ""
    trophies: int = 0
    required_trophies: int = 0
    members: list[BrawlStarsClubMember] = Field(default_factory=list)


class BrawlStarsEvent(BaseModel):
    """A single event in the rotation."""

    start_time: str = ""
    end_time: str = ""
    event: BattleEvent = Field(default_factory=BattleEvent)


class BrawlerDefinition(BaseModel):
    """Brawler definition from the brawlers list endpoint."""

    id: int = 0
    name: str = ""
    star_powers: list[BrawlerStarPower] = Field(default_factory=list)
    gadgets: list[BrawlerGadget] = Field(default_factory=list)


class BrawlersList(BaseModel):
    """Response from the brawlers list endpoint."""

    items: list[BrawlerDefinition] = Field(default_factory=list)


# ---- Service class ----


class BrawlStarsService:
    """Typed HTTP client for the Brawl Stars API.

    Centralizes all Brawl Stars API calls into a single session-managed
    service with Pydantic-validated responses and shared rate-limit handling.
    """

    BASE_URL = "https://api.brawlstars.com/v1"

    def __init__(self) -> None:
        self._token: str | None = brawlstarsToken
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _request(
        self,
        path: str,
        params: dict[str, str] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any] | list[dict[str, Any]] | None:
        """Make an authenticated GET request to the Brawl Stars API with retry logic.

        Implements exponential backoff with jitter for rate limits (HTTP 429) and
        server errors (HTTP 503). Respects Retry-After header when present.
        """
        if not self._token:
            return None
        session = await self._ensure_session()
        url = f"{self.BASE_URL}/{path}"
        headers = {"Authorization": f"Bearer {self._token}"}

        for attempt in range(max_retries + 1):
            async with session.get(
                url,
                headers=headers,
                params=params,
                timeout=ClientTimeout(total=10),
            ) as response:
                if response.status == 200:
                    raw: Any = await response.json()
                    if isinstance(raw, dict):
                        return raw
                    if isinstance(raw, list):
                        return raw
                    return None

                # Read response body for logging
                try:
                    body = await response.text()
                except Exception:
                    body = "<unable to read body>"

                # Handle rate limits and server errors with retry
                if response.status in (429, 503) and attempt < max_retries:
                    # Check for Retry-After header
                    retry_after = response.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        delay = int(retry_after)
                    else:
                        # Exponential backoff with jitter: 2^attempt * (0.5 to 1.5)
                        base_delay = 2 ** attempt
                        jitter = random.uniform(0.5, 1.5)
                        delay = base_delay * jitter

                    logger.warning(
                        f"Rate limit/server error on {path} (attempt {attempt + 1}/{max_retries + 1}): "
                        f"HTTP {response.status}. Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)
                    continue

                # Log and return None for all error cases after retries exhausted
                logger.error(
                    f"Request to {path} failed with HTTP {response.status}: {body[:200]}"
                )
                return None

        return None

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_player(self, tag: str) -> BrawlStarsPlayer | None:
        """Fetch a player profile by tag."""
        clean_tag = tag.lstrip("#")
        data = await self._request(f"players/%23{clean_tag}")
        if data is None:
            return None
        return BrawlStarsPlayer(
            tag=data.get("tag", ""),
            name=data.get("name", ""),
            name_color=data.get("nameColor", ""),
            trophies=data.get("trophies", 0),
            highest_trophies=data.get("highestTrophies", data.get("highest_trophies", 0)),
            exp_level=data.get("expLevel", data.get("exp_level", 0)),
            exp_points=data.get("expPoints", data.get("exp_points", 0)),
            is_qualified_from_championship=data.get(
                "isQualifiedFromChampionship",
                data.get("is_qualified_from_championship", False),
            ),
            solo_victories=data.get("soloVictories", data.get("solo_victories", 0)),
            duo_victories=data.get("duoVictories", data.get("duo_victories", 0)),
            x3vs3_victories=data.get("3vs3Victories", data.get("x3v3Victories", 0)),
            club=BrawlStarsClub(
                tag=data.get("club", {}).get("tag", ""),
                name=data.get("club", {}).get("name", ""),
            )
            if data.get("club")
            else None,
            brawlers=[
                BrawlerInfo(
                    id=b.get("id", 0),
                    name=b.get("name", ""),
                    power=b.get("power", 1),
                    rank=b.get("rank", 1),
                    trophies=b.get("trophies", 0),
                    highest_trophies=b.get("highestTrophies", b.get("highest_trophies", 0)),
                    gears=[
                        BrawlerGear(id=g.get("id", 0), name=g.get("name", ""), level=g.get("level", 1))
                        for g in b.get("gears", [])
                    ],
                    gadgets=[
                        BrawlerGadget(id=g.get("id", 0), name=g.get("name", ""))
                        for g in b.get("gadgets", [])
                    ],
                    star_powers=[
                        BrawlerStarPower(id=sp.get("id", 0), name=sp.get("name", ""))
                        for sp in b.get("starPowers", b.get("star_powers", []))
                    ],
                )
                for b in data.get("brawlers", [])
            ],
        )

    async def get_battle_log(self, tag: str) -> list[BattleLogItem] | None:
        """Fetch a player's battle log."""
        clean_tag = tag.lstrip("#")
        data = await self._request(f"players/%23{clean_tag}/battlelog")
        if data is None:
            return None
        # Handle both dict response with "items" key and direct list response
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("items", [])
        else:
            items = []
        if not items:
            return []
        return [
            BattleLogItem(
                battle_time=item.get("battleTime", item.get("battle_time", "")),
                event=BattleEvent(
                    mode=item.get("event", {}).get("mode", ""),
                    map=item.get("event", {}).get("map", ""),
                    id=item.get("event", {}).get("id", 0),
                ),
                battle=self._parse_battle(item.get("battle", {})),
            )
            for item in items
        ]

    def _parse_battle(self, battle: dict[str, Any]) -> BattleResult:
        """Parse a raw battle dict into a BattleResult model."""
        result = BattleResult(
            mode=battle.get("mode", ""),
            type=battle.get("type", ""),
            result=battle.get("result", ""),
            duration=battle.get("duration"),
            trophy_change=battle.get("trophyChange", battle.get("trophy_change")),
        )

        if "brawler" in battle:
            result.brawler = BattleBrawler(
                name=battle["brawler"].get("name", ""),
                power=battle["brawler"].get("power", 1),
                trophies=battle["brawler"].get("trophies", 0),
            )

        if "starPlayer" in battle or "star_player" in battle:
            sp = battle.get("starPlayer") or battle.get("star_player", {})
            result.star_player = BattlePlayer(
                tag=sp.get("tag", ""),
                name=sp.get("name", ""),
                brawler=BattleBrawler(
                    name=sp.get("brawler", {}).get("name", ""),
                    power=sp.get("brawler", {}).get("power", 1),
                    trophies=sp.get("brawler", {}).get("trophies", 0),
                ),
            )

        if "players" in battle:
            result.players = [
                BattlePlayer(
                    tag=p.get("tag", ""),
                    name=p.get("name", ""),
                    brawler=BattleBrawler(
                        name=p.get("brawler", {}).get("name", ""),
                        power=p.get("brawler", {}).get("power", 1),
                        trophies=p.get("brawler", {}).get("trophies", 0),
                    ),
                )
                for p in battle["players"]
            ]

        if "teams" in battle:
            result.teams = [
                [
                    BattlePlayer(
                        tag=p.get("tag", ""),
                        name=p.get("name", ""),
                        brawler=BattleBrawler(
                            name=p.get("brawler", {}).get("name", ""),
                            power=p.get("brawler", {}).get("power", 1),
                            trophies=p.get("brawler", {}).get("trophies", 0),
                        ),
                    )
                    for p in team
                ]
                for team in battle["teams"]
            ]

        return result

    async def get_club(self, tag: str) -> BrawlStarsClubFull | None:
        """Fetch a club profile by tag."""
        clean_tag = tag.lstrip("#")
        data = await self._request(f"clubs/%23{clean_tag}")
        if data is None:
            return None
        return BrawlStarsClubFull(
            tag=data.get("tag", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            trophies=data.get("trophies", 0),
            required_trophies=data.get("requiredTrophies", data.get("required_trophies", 0)),
            members=[
                BrawlStarsClubMember(
                    tag=m.get("tag", ""),
                    name=m.get("name", ""),
                    trophies=m.get("trophies", 0),
                    role=m.get("role", "member"),
                )
                for m in data.get("members", [])
            ],
        )

    async def get_events(self) -> list[BrawlStarsEvent] | None:
        """Fetch the current event rotation."""
        data = await self._request("events/rotation")
        if data is None:
            return None
        items: list[dict[str, Any]] = data if isinstance(data, list) else data.get("items", [])
        if not items:
            return []
        return [
            BrawlStarsEvent(
                start_time=item.get("startTime", item.get("start_time", "")),
                end_time=item.get("endTime", item.get("end_time", "")),
                event=BattleEvent(
                    mode=item.get("event", {}).get("mode", ""),
                    map=item.get("event", {}).get("map", ""),
                    id=item.get("event", {}).get("id", 0),
                ),
            )
            for item in items
        ]

    async def get_brawlers_list(self) -> BrawlersList | None:
        """Fetch the full list of brawler definitions."""
        data = await self._request("brawlers")
        if data is None:
            return None
        items = data.get("items", [])
        return BrawlersList(
            items=[
                BrawlerDefinition(
                    id=b.get("id", 0),
                    name=b.get("name", ""),
                    star_powers=[
                        BrawlerStarPower(id=sp.get("id", 0), name=sp.get("name", ""))
                        for sp in b.get("starPowers", b.get("star_powers", []))
                    ],
                    gadgets=[
                        BrawlerGadget(id=g.get("id", 0), name=g.get("name", ""))
                        for g in b.get("gadgets", [])
                    ],
                )
                for b in items
            ],
        )

    # ---- Account linking helpers (database-backed) ----

    async def get_linked_account(self, user_id: str) -> str | None:
        """Get the Brawl Stars tag linked to a Discord user."""
        from api import get_brawlstars_linked_account

        return await get_brawlstars_linked_account(user_id)

    async def link_account(self, user_id: str, brawlstars_tag: str) -> None:
        """Link a Brawl Stars tag to a Discord user."""
        from api import add_brawlstars_linked_account

        await add_brawlstars_linked_account(user_id, brawlstars_tag)

    async def unlink_account(self, user_id: str) -> None:
        """Remove the Brawl Stars link for a Discord user."""
        from api import remove_brawlstars_linked_account

        await remove_brawlstars_linked_account(user_id)
