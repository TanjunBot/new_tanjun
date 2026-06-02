import logging

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
    push_url = _build_push_url(max(0, int(client.latency * 1000)))
    if push_url is None:
        return

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
