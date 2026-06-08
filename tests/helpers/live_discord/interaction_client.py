from __future__ import annotations

import base64
import json
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp

from tests.helpers.live_discord.rate_limit import raise_for_rate_limit

DEFAULT_CLIENT_BUILD = 360320
INTERACTION_API_VERSIONS = ("v10", "v9")


def _super_properties(*, client_build: int = DEFAULT_CLIENT_BUILD) -> str:
    payload = {
        "os": "Linux",
        "browser": "Chrome",
        "device": "",
        "system_locale": "en-US",
        "browser_user_agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "browser_version": "120.0.0.0",
        "os_version": "",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": client_build,
        "client_event_source": None,
    }
    return base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()


def _interaction_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": token.strip(),
        "Content-Type": "application/json",
        "X-Super-Properties": _super_properties(),
        "X-Discord-Locale": "en-US",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }


class InteractionInvokeError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status: int,
        body: str,
        version_mismatch: bool = False,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.body = body
        self.version_mismatch = version_mismatch


def _is_version_mismatch(status: int, body: str) -> bool:
    if status != 400:
        return False
    lowered = body.lower()
    return "version" in lowered or "unknown integration" in lowered


async def _post_interaction(
    token: str,
    payload: dict[str, Any],
    *,
    api_version: str,
) -> tuple[int, str, Any]:
    url = f"https://discord.com/api/{api_version}/interactions"
    async with (
        aiohttp.ClientSession() as session,
        session.post(url, headers=_interaction_headers(token), json=payload) as resp,
    ):
        body = await resp.text()
        return resp.status, body, resp.headers


async def invoke_application_command(
    token: str,
    payload: dict[str, Any],
    *,
    preferred_api_version: str = "v10",
    retry_count: int = 2,
    on_refresh: Callable[[], Awaitable[None]] | None = None,
    rebuild_payload: Callable[[], dict[str, Any]] | None = None,
) -> None:
    versions = [preferred_api_version]
    for version in INTERACTION_API_VERSIONS:
        if version not in versions:
            versions.append(version)

    current_payload = payload
    last_status = 0
    last_body = ""

    for attempt in range(retry_count + 1):
        for api_version in versions:
            status, body, headers = await _post_interaction(
                token,
                current_payload,
                api_version=api_version,
            )
            last_status, last_body = status, body
            if status == 204:
                return
            if status == 404 and api_version != versions[-1]:
                continue
            raise_for_rate_limit(
                status=status,
                payload=body,
                headers=headers,
                action=f"POST /{api_version}/interactions",
            )
            if status in (401, 403):
                raise RuntimeError(
                    f"User token rejected ({status}). "
                    "Re-run: python scripts/e2e_discord_login.py"
                )
            version_mismatch = _is_version_mismatch(status, body)
            if version_mismatch and on_refresh and rebuild_payload and attempt < retry_count:
                await on_refresh()
                current_payload = rebuild_payload()
                break
            if api_version == versions[-1]:
                raise InteractionInvokeError(
                    f"POST /{api_version}/interactions -> {status}: {body[:500]}",
                    status=status,
                    body=body,
                    version_mismatch=version_mismatch,
                )
        else:
            continue
        continue

    raise InteractionInvokeError(
        f"POST /interactions -> {last_status}: {last_body[:500]}",
        status=last_status,
        body=last_body,
    )
