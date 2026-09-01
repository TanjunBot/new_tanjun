import logging
import math

import aiohttp
from aiohttp import ClientTimeout
from discord import Client

import config

logger = logging.getLogger(__name__)


def _build_push_url(latency_ms: int) -> str | None:
    token = config.UPTIME_KUMA_PUSH_TOKEN.strip()
    if not token:
        return None
    base = config.UPTIME_KUMA_STATUS_URL
    return f"{base}/api/push/{token}?status=up&msg=OK&ping={latency_ms}"


async def ping_server(client: Client) -> None:
    if client is None or client.user is None:
        return
    latency_ms = int(client.latency * 1000) if math.isfinite(client.latency) else 0

    # 1. Uptime Kuma Push
    push_url = _build_push_url(max(0, latency_ms))
    if push_url is not None:
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.get(push_url, timeout=ClientTimeout(total=10)) as response,
            ):
                if response.status == 200:
                    logger.debug("Uptime Kuma push succeeded")
                else:
                    logger.warning("Uptime Kuma push failed, status code: %s", response.status)
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Uptime Kuma push error: %s", exc)

    # 2. Botstatus API Heartbeat
    botstatus_url = getattr(config, "BOTSTATUS_API_URL", "").strip()
    if botstatus_url:
        payload = {
            "id": str(client.user.id),
            "status": "alive",
            "latency": client.latency if math.isfinite(client.latency) else 0.0,
            "latency_ms": max(0, latency_ms),
            "guild_count": len(client.guilds) if hasattr(client, "guilds") else None,
            "version": getattr(config, "version", None),
        }
        headers = {}
        token = getattr(config, "BOTSTATUS_API_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            async with (
                aiohttp.ClientSession() as session,
                session.post(botstatus_url, json=payload, headers=headers, timeout=ClientTimeout(total=10)) as response,
            ):
                if response.status in (200, 201, 204):
                    logger.debug("Botstatus API push succeeded")
                else:
                    logger.warning("Botstatus API push failed, status code: %s", response.status)
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Botstatus API push error: %s", exc)
