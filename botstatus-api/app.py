"""Botstatus API microservice for Tanjun Bot.

Receives periodic heartbeats from Tanjun bot(s) and provides:
- Health check endpoints
- REST status API
- Prometheus metrics
- Shields.io badge API
- Optional Uptime Kuma push forwarding
"""

from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hmac
import json
import logging
import math
import os
from pathlib import Path
from time import monotonic
from typing import Any

from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Path as FastAPIPath,
    Query,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("botstatus-api")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOTSTATUS_")

    host: str = "0.0.0.0"
    port: int = 8000
    timeout_seconds: int = 90  # Mark bot as offline if no ping for 90s
    api_key: str = ""  # Required for POST / heartbeat
    default_bot_id: str = "832297321793323028"  # Tanjun bot ID
    state_file: str = "data/state.json"
    uptime_kuma_push_url: str = ""
    max_body_bytes: int = 64 * 1024
    heartbeat_rate_limit: int = 60
    heartbeat_rate_window_seconds: int = 60

settings = Settings()


class HeartbeatPayload(BaseModel):
    id: str = Field(..., pattern=r"^[0-9]{15,20}$", description="Discord application / bot user ID")
    status: str = Field(default="alive", min_length=1, max_length=32, description="Status string, e.g. alive / online")
    latency: float | str | None = Field(default=None, description="Discord WebSocket latency in seconds")
    latency_ms: int | None = Field(default=None, ge=0, le=300_000, description="Discord WebSocket latency in milliseconds")
    guild_count: int | None = Field(default=None, ge=0, description="Number of connected Discord guilds")
    version: str | None = Field(default=None, max_length=128, description="Bot version")
    extra: dict[str, Any] | None = Field(default=None, description="Extra metadata")

    @model_validator(mode="after")
    def validate_values(self) -> "HeartbeatPayload":
        if isinstance(self.latency, float) and not math.isfinite(self.latency):
            raise ValueError("latency must be finite")
        if self.latency is not None:
            if isinstance(self.latency, str) and len(self.latency) > 32:
                raise ValueError("latency is too long")
            try:
                parsed = float(self.latency)
            except (TypeError, ValueError) as exc:
                raise ValueError("latency must be numeric") from exc
            if parsed < 0 or parsed > 300:
                raise ValueError("latency must be between 0 and 300 seconds")
        if self.extra is not None and len(json.dumps(self.extra, separators=(",", ":"))) > 8 * 1024:
            raise ValueError("extra metadata is too large")
        return self


class BotState(BaseModel):
    id: str
    status: str  # "online" | "offline"
    raw_status: str
    latency_ms: int
    guild_count: int | None = None
    version: str | None = None
    last_ping: str
    last_ping_timestamp: float
    seconds_since_last_ping: int = 0
    extra: dict[str, Any] | None = None


class StatusManager:
    def __init__(self, state_file: str, timeout_seconds: int) -> None:
        self.state_file = Path(state_file)
        self.timeout_seconds = timeout_seconds
        self.bots: dict[str, dict[str, Any]] = {}
        self.load_state()

    def load_state(self) -> None:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    self.bots = json.load(f)
                logger.info("Loaded state for %d bot(s) from %s", len(self.bots), self.state_file)
            except Exception as e:
                logger.warning("Failed to load state from %s: %s", self.state_file, e)

    def save_state(self) -> None:
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.bots, f, indent=2)
        except Exception as e:
            logger.warning("Failed to save state to %s: %s", self.state_file, e)

    def record_ping(self, payload: HeartbeatPayload) -> BotState:
        now = datetime.now(timezone.utc)
        now_ts = now.timestamp()

        # Parse latency
        latency_ms = 0
        if payload.latency_ms is not None:
            latency_ms = payload.latency_ms
        elif payload.latency is not None:
            try:
                lat_float = float(payload.latency)
                latency_ms = max(0, int(lat_float * 1000)) if lat_float < 10.0 else int(lat_float)
            except (ValueError, TypeError):
                latency_ms = 0

        bot_data = {
            "id": payload.id,
            "status": "online",
            "raw_status": payload.status,
            "latency_ms": latency_ms,
            "guild_count": payload.guild_count,
            "version": payload.version,
            "last_ping": now.isoformat(),
            "last_ping_timestamp": now_ts,
            "extra": payload.extra,
        }
        self.bots[payload.id] = bot_data
        self.save_state()
        return self.get_bot(payload.id)

    def get_bot(self, bot_id: str) -> BotState | None:
        data = self.bots.get(bot_id)
        if not data:
            return None

        now_ts = datetime.now(timezone.utc).timestamp()
        last_ts = data.get("last_ping_timestamp", 0)
        seconds_ago = int(max(0, now_ts - last_ts))
        is_online = seconds_ago <= self.timeout_seconds and data.get("raw_status", "").lower() in ("alive", "online", "ok", "up")

        return BotState(
            id=data["id"],
            status="online" if is_online else "offline",
            raw_status=data.get("raw_status", "unknown"),
            latency_ms=data.get("latency_ms", 0),
            guild_count=data.get("guild_count"),
            version=data.get("version"),
            last_ping=data.get("last_ping", ""),
            last_ping_timestamp=last_ts,
            seconds_since_last_ping=seconds_ago,
            extra=data.get("extra"),
        )

    def get_all(self) -> list[BotState]:
        return [self.get_bot(bid) for bid in self.bots if self.get_bot(bid) is not None]

    def get_primary_bot(self) -> BotState | None:
        if settings.default_bot_id in self.bots:
            return self.get_bot(settings.default_bot_id)
        all_bots = self.get_all()
        return all_bots[0] if all_bots else None


manager = StatusManager(settings.state_file, settings.timeout_seconds)
_heartbeat_requests: dict[str, deque[float]] = defaultdict(deque)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Botstatus API started on %s:%d", settings.host, settings.port)
    yield
    manager.save_state()
    logger.info("Botstatus API shutdown.")


app = FastAPI(
    title="Tanjun Botstatus API",
    description="Heartbeat ingest, status reporting and metrics for Tanjun Discord Bot",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def reject_oversized_requests(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            too_large = int(content_length) > settings.max_body_bytes
        except ValueError:
            too_large = True
        if too_large:
            return Response(
                content='{"detail":"Request body too large"}',
                status_code=413,
                media_type="application/json",
            )
    return await call_next(request)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_auth(authorization: str | None = Header(None)) -> None:
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Heartbeat authentication is not configured",
        )
    scheme, separator, provided = (authorization or "").partition(" ")
    if not separator or scheme.lower() != "bearer" or not provided.strip():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")
    expected = settings.api_key.removeprefix("Bearer ").strip()
    provided = provided.strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")


def enforce_heartbeat_rate_limit(client_key: str) -> None:
    now = monotonic()
    requests = _heartbeat_requests[client_key]
    cutoff = now - settings.heartbeat_rate_window_seconds
    while requests and requests[0] <= cutoff:
        requests.popleft()
    if len(requests) >= settings.heartbeat_rate_limit:
        retry_after = max(1, int(requests[0] + settings.heartbeat_rate_window_seconds - now))
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Heartbeat rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )
    requests.append(now)


def _escape_prometheus_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


# ── Heartbeat Ingest ─────────────────────────────────────────────────────────

@app.post("/", status_code=status.HTTP_200_OK)
@app.post("/api/status", status_code=status.HTTP_200_OK)
@app.post("/status", status_code=status.HTTP_200_OK)
async def post_heartbeat(
    payload: HeartbeatPayload,
    request: Request,
    authorization: str | None = Header(None),
) -> dict[str, Any]:
    verify_auth(authorization)
    enforce_heartbeat_rate_limit(request.client.host if request.client else "unknown")
    bot = manager.record_ping(payload)
    logger.info("Heartbeat received from bot %s: latency=%dms", payload.id, bot.latency_ms)

    # Optional Uptime Kuma Push forwarding
    if settings.uptime_kuma_push_url:
        try:
            import httpx

            push_url = settings.uptime_kuma_push_url
            if "?" in push_url:
                push_url += f"&status=up&msg=OK&ping={bot.latency_ms}"
            else:
                push_url += f"?status=up&msg=OK&ping={bot.latency_ms}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.get(push_url)
        except Exception as e:
            # The configured push URL contains the Uptime Kuma secret token.
            logger.warning("Failed to forward heartbeat to Uptime Kuma: %s", type(e).__name__)

    return {"status": "ok", "bot": bot.model_dump()}


# ── Status Query Endpoints ───────────────────────────────────────────────────

@app.get("/")
@app.get("/status")
async def get_status(
    bot_id: str | None = Query(None, pattern=r"^[0-9]{15,20}$", description="Optional bot ID"),
) -> dict[str, Any]:
    if bot_id:
        bot = manager.get_bot(bot_id)
        if not bot:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
        return bot.model_dump()

    primary = manager.get_primary_bot()
    all_bots = manager.get_all()
    overall_status = "online" if primary and primary.status == "online" else ("online" if any(b.status == "online" for b in all_bots) else "offline")

    return {
        "status": overall_status,
        "primary_bot": primary.model_dump() if primary else None,
        "bots": [b.model_dump() for b in all_bots],
        "total_bots": len(all_bots),
        "online_bots": sum(1 for b in all_bots if b.status == "online"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/status/{bot_id}")
async def get_bot_status(
    bot_id: str = FastAPIPath(..., pattern=r"^[0-9]{15,20}$"),
) -> dict[str, Any]:
    bot = manager.get_bot(bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bot {bot_id} not found")
    return bot.model_dump()


# ── Health & Liveness ────────────────────────────────────────────────────────

@app.get("/health")
@app.get("/livez")
@app.get("/readyz")
async def health_check() -> dict[str, Any]:
    primary = manager.get_primary_bot()
    is_up = primary.status == "online" if primary else True  # Healthy if service is up
    return {
        "status": "healthy" if is_up else "degraded",
        "service": "botstatus-api",
        "bot_online": primary.status == "online" if primary else False,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Shields.io Badge API ─────────────────────────────────────────────────────

@app.get("/badge")
@app.get("/badge/{bot_id}")
async def get_badge(bot_id: str | None = None) -> dict[str, Any]:
    target_id = bot_id or settings.default_bot_id
    bot = manager.get_bot(target_id) or manager.get_primary_bot()

    if bot and bot.status == "online":
        return {
            "schemaVersion": 1,
            "label": "Tanjun",
            "message": f"online ({bot.latency_ms}ms)",
            "color": "brightgreen",
        }
    return {
        "schemaVersion": 1,
        "label": "Tanjun",
        "message": "offline",
        "color": "red",
    }


# ── Prometheus Metrics ───────────────────────────────────────────────────────

@app.get("/metrics")
async def metrics() -> Response:
    lines = [
        "# HELP bot_online Whether the bot is online (1) or offline (0)",
        "# TYPE bot_online gauge",
    ]
    for b in manager.get_all():
        val = 1 if b.status == "online" else 0
        lines.append(f'bot_online{{bot_id="{_escape_prometheus_label(b.id)}"}} {val}')

    lines.extend([
        "# HELP bot_latency_ms Bot WebSocket latency in milliseconds",
        "# TYPE bot_latency_ms gauge",
    ])
    for b in manager.get_all():
        lines.append(f'bot_latency_ms{{bot_id="{_escape_prometheus_label(b.id)}"}} {b.latency_ms}')

    lines.extend([
        "# HELP bot_seconds_since_last_ping Seconds since last heartbeat was received",
        "# TYPE bot_seconds_since_last_ping gauge",
    ])
    for b in manager.get_all():
        lines.append(f'bot_seconds_since_last_ping{{bot_id="{_escape_prometheus_label(b.id)}"}} {b.seconds_since_last_ping}')

    if any(b.guild_count is not None for b in manager.get_all()):
        lines.extend([
            "# HELP bot_guild_count Connected Discord guild count",
            "# TYPE bot_guild_count gauge",
        ])
        for b in manager.get_all():
            if b.guild_count is not None:
                lines.append(f'bot_guild_count{{bot_id="{_escape_prometheus_label(b.id)}"}} {b.guild_count}')

    content = "\n".join(lines) + "\n"
    return Response(content=content, media_type="text/plain; version=0.0.4")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
