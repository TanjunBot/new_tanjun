from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from tests.helpers.live_discord.rate_limit import raise_for_rate_limit

API_BASE = "https://discord.com/api/v10"
USER_AGENT = "TanjunBot-E2E/1.0 (live tests)"
BOT_INVITE_SCOPES = "bot applications.commands"

# View channel + send messages + embed links + read message history (shorter OAuth scroll list).
_DEFAULT_BOT_PERMISSIONS = "84992"


def bot_invite_permissions() -> str:
    return os.getenv("TANJUN_E2E_BOT_PERMISSIONS", _DEFAULT_BOT_PERMISSIONS).strip()




def _request(
    method: str,
    path: str,
    token: str,
    *,
    body: dict | None = None,
) -> object:
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status == 204:
                return None
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode(errors="replace")
        raise_for_rate_limit(
            status=exc.code,
            payload=payload,
            headers=exc.headers,
            action=f"{method} {path}",
        )
        raise RuntimeError(f"{method} {path} -> {exc.code}: {payload}") from exc


def bot_is_guild_member(bot_token: str, guild_id: str, bot_user_id: str) -> bool:
    url = f"{API_BASE}/guilds/{guild_id}/members/{bot_user_id}"
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bot {bot_token.strip()}",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        payload = exc.read().decode(errors="replace")
        raise_for_rate_limit(
            status=exc.code,
            payload=payload,
            headers=exc.headers,
            action=f"GET /guilds/{guild_id}/members/{bot_user_id}",
        )
        raise RuntimeError(
            f"GET /guilds/{guild_id}/members/{bot_user_id} -> {exc.code}: {payload}"
        ) from exc


def fetch_bot_user(bot_token: str) -> dict:
    data = _request("GET", "/users/@me", f"Bot {bot_token.strip()}")
    if not isinstance(data, dict):
        raise RuntimeError("GET /users/@me (bot) returned unexpected payload")
    return data


def fetch_me(token: str) -> dict:
    data = _request("GET", "/users/@me", token)
    if not isinstance(data, dict):
        raise RuntimeError("GET /users/@me returned unexpected payload")
    return data


def create_guild(token: str, name: str) -> dict:
    data = _request("POST", "/users/@me/guilds", token, body={"name": name})
    if not isinstance(data, dict):
        raise RuntimeError("POST /users/@me/guilds returned unexpected payload")
    return data


def default_text_channel_id(guild: dict) -> str:
    for channel in guild.get("channels") or []:
        if channel.get("type") == 0:
            return str(channel["id"])
    raise RuntimeError("Created guild has no text channel in response")


def default_text_channel_id_for_guild(bot_token: str, guild_id: str) -> str:
    data = _request("GET", f"/guilds/{guild_id}/channels", f"Bot {bot_token.strip()}")
    if not isinstance(data, list):
        raise RuntimeError(f"GET /guilds/{guild_id}/channels returned unexpected payload")
    text_channels = [ch for ch in data if isinstance(ch, dict) and ch.get("type") == 0]
    if not text_channels:
        raise RuntimeError(f"Guild {guild_id} has no text channels visible to the bot")
    for preferred_name in ("general", "allgemein", "chat"):
        for channel in text_channels:
            if str(channel.get("name", "")).lower() == preferred_name:
                return str(channel["id"])
    text_channels.sort(key=lambda ch: int(ch.get("position", 0)))
    return str(text_channels[0]["id"])


def delete_guild(token: str, guild_id: str) -> None:
    try:
        _request("DELETE", f"/guilds/{guild_id}", token)
    except RuntimeError as exc:
        if "404" in str(exc):
            return
        raise


def _oauth_authorize_query(
    *,
    application_id: str,
    guild_id: str,
    permissions: str | None = None,
) -> str:
    permissions = permissions or bot_invite_permissions()
    return urllib.parse.urlencode(
        {
            "client_id": application_id,
            "scope": BOT_INVITE_SCOPES,
            "permissions": permissions,
            "guild_id": guild_id,
            "disable_guild_select": "true",
        }
    )


def authorize_bot_to_guild(
    token: str,
    *,
    application_id: str,
    guild_id: str,
    permissions: str | None = None,
) -> None:
    permissions = permissions or bot_invite_permissions()
    query = _oauth_authorize_query(
        application_id=application_id,
        guild_id=guild_id,
        permissions=permissions,
    )
    url = f"{API_BASE}/oauth2/authorize?{query}"
    payload = json.dumps(
        {
            "authorize": True,
            "guild_id": guild_id,
            "permissions": permissions,
            "integration_type": 0,
        }
    ).encode()
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": token.strip(),
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Origin": "https://discord.com",
            "Referer": f"https://discord.com/oauth2/authorize?{query}",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
        headers = exc.headers

    if status in (200, 201, 204):
        return
    if status in (301, 302, 303, 307, 308):
        return

    body = raw.decode(errors="replace") if raw else ""
    raise_for_rate_limit(
        status=status,
        payload=body,
        headers=headers,
        action="POST /oauth2/authorize",
    )
    raise RuntimeError(f"POST /oauth2/authorize -> {status}: {body}")
