from __future__ import annotations

import asyncio
import contextlib
import time
from dataclasses import dataclass
from typing import Any

import aiohttp

from tests.helpers.live_discord.rate_limit import (
    DiscordRateLimitedError,
    raise_for_rate_limit,
    retry_after_from_headers,
    retry_after_from_payload,
)

API_BASE = "https://discord.com/api/v10"


@dataclass(frozen=True)
class GuildContext:
    guild_id: str
    channel_id: str
    owner_user_id: str


class DiscordUserClient:
    def __init__(self, token: str) -> None:
        raw = token.strip()
        if raw.lower().startswith("bot "):
            raise RuntimeError(
                "TANJUN_E2E_USER_TOKEN must be the test USER token from browser DevTools, "
                "not the bot token (do not use TANJUN_TEST_BOT_TOKEN here)."
            )
        self._token = raw

    @staticmethod
    def ensure_human_account(me: dict[str, Any]) -> None:
        if me.get("bot"):
            raise RuntimeError(
                "TANJUN_E2E_USER_TOKEN is a bot account. "
                "Use your dedicated test USER token from browser DevTools (authorization header)."
            )

    def _headers(self) -> dict[str, str]:
        return {"Authorization": self._token, "Content-Type": "application/json"}

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        expected: tuple[int, ...] = (200, 201, 204),
    ) -> Any:
        url = f"{API_BASE}{path}"
        async with (
            aiohttp.ClientSession() as session,
            session.request(method, url, headers=self._headers(), json=json) as resp,
        ):
            body: Any = None
            if resp.status != 204:
                body = await resp.json(content_type=None)
            if resp.status not in expected:
                payload = "" if body is None else str(body)
                raise_for_rate_limit(
                    status=resp.status,
                    payload=payload,
                    headers=resp.headers,
                    action=f"{method} {path}",
                )
                raise RuntimeError(f"{method} {path} -> {resp.status}: {body}")
            return body

    async def me(self) -> dict[str, Any]:
        data = await self.request("GET", "/users/@me")
        assert isinstance(data, dict)
        return data

    async def try_create_guild(self, name: str) -> dict[str, Any] | None:
        url = f"{API_BASE}/users/@me/guilds"
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url,
                headers=self._headers(),
                json={"name": name},
            ) as resp,
        ):
            body = await resp.json(content_type=None) if resp.status != 204 else None
            if resp.status in (200, 201) and isinstance(body, dict):
                return body
            if resp.status in (403, 405):
                return None
            raise RuntimeError(f"POST /users/@me/guilds -> {resp.status}: {body}")

    async def delete_guild(self, guild_id: str) -> None:
        await self.request("DELETE", f"/guilds/{guild_id}", expected=(204, 404))

    async def authorize_bot_to_guild(
        self,
        *,
        application_id: str,
        guild_id: str,
        permissions: str = "2147483648",
    ) -> None:
        from urllib.parse import urlencode

        query = urlencode(
            {
                "client_id": application_id,
                "scope": "bot applications.commands",
                "permissions": permissions,
                "guild_id": guild_id,
                "disable_guild_select": "true",
            }
        )
        referer = f"https://discord.com/oauth2/authorize?{query}"
        url = f"{API_BASE}/oauth2/authorize?{query}"
        async with (
            aiohttp.ClientSession() as session,
            session.post(
                url,
                headers={
                    **self._headers(),
                    "Origin": "https://discord.com",
                    "Referer": referer,
                },
                json={
                    "authorize": True,
                    "guild_id": guild_id,
                    "permissions": permissions,
                    "integration_type": 0,
                },
                allow_redirects=False,
            ) as resp,
        ):
            if resp.status in (200, 201, 204, 301, 302, 303, 307, 308):
                return
            body = await resp.text()
            raise RuntimeError(f"POST /oauth2/authorize -> {resp.status}: {body}")

    async def list_guild_channels(self, guild_id: str) -> list[dict[str, Any]]:
        data = await self.request("GET", f"/guilds/{guild_id}/channels")
        assert isinstance(data, list)
        return data

    async def default_text_channel_id(self, guild_id: str) -> str:
        channels = await self.list_guild_channels(guild_id)
        for channel in channels:
            if channel.get("type") == 0 and channel.get("position", 0) == 0:
                return str(channel["id"])
        for channel in channels:
            if channel.get("type") == 0:
                return str(channel["id"])
        raise RuntimeError(f"No text channel in guild {guild_id}")


class DiscordBotClient:
    def __init__(self, token: str, application_id: str) -> None:
        self._token = token
        self._application_id = application_id

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bot {self._token}"}

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        expected: tuple[int, ...] = (200, 201, 204),
        max_rate_limit_retries: int = 8,
    ) -> Any:
        url = f"{API_BASE}{path}"
        for attempt in range(max_rate_limit_retries + 1):
            async with (
                aiohttp.ClientSession() as session,
                session.request(method, url, headers=self._headers(), params=params) as resp,
            ):
                body: Any = None
                if resp.status != 204:
                    body = await resp.json(content_type=None)
                if resp.status in expected:
                    return body
                payload = "" if body is None else str(body)
                if resp.status == 429 and attempt < max_rate_limit_retries:
                    retry_after = (
                        retry_after_from_headers(resp.headers)
                        or retry_after_from_payload(payload)
                        or 1.0
                    )
                    await asyncio.sleep(max(retry_after, 0.5))
                    continue
                raise_for_rate_limit(
                    status=resp.status,
                    payload=payload,
                    headers=resp.headers,
                    action=f"{method} {path}",
                )
                raise RuntimeError(f"{method} {path} -> {resp.status}: {body}")
        raise RuntimeError(f"{method} {path} exhausted rate-limit retries")

    async def guild_has_member(self, guild_id: str, user_id: str) -> bool:
        try:
            await self.request("GET", f"/guilds/{guild_id}/members/{user_id}")
            return True
        except RuntimeError:
            return False

    async def wait_for_bot_member(self, guild_id: str, bot_user_id: str, timeout_sec: float) -> None:
        deadline = time.monotonic() + timeout_sec
        poll_sec = 5.0
        while time.monotonic() < deadline:
            try:
                if await self.guild_has_member(guild_id, bot_user_id):
                    return
            except DiscordRateLimitedError:
                raise
            await asyncio.sleep(poll_sec)
        raise RuntimeError(f"Bot {bot_user_id} did not join guild {guild_id} in time")

    async def list_global_commands(self) -> list[dict[str, Any]]:
        data = await self.request("GET", f"/applications/{self._application_id}/commands")
        assert isinstance(data, list)
        return data

    async def list_guild_commands(self, guild_id: str) -> list[dict[str, Any]]:
        data = await self.request(
            "GET",
            f"/applications/{self._application_id}/guilds/{guild_id}/commands",
        )
        assert isinstance(data, list)
        return data

    async def collect_command_names(self, *, guild_id: str | None = None) -> set[str]:
        names: set[str] = set()
        with contextlib.suppress(RuntimeError, DiscordRateLimitedError):
            for cmd in await self.list_global_commands():
                names.add(str(cmd.get("name", "")))
        if guild_id:
            with contextlib.suppress(RuntimeError, DiscordRateLimitedError):
                for cmd in await self.list_guild_commands(guild_id):
                    names.add(str(cmd.get("name", "")))
        names.discard("")
        return names

    async def wait_for_application_command_names(
        self,
        required: set[str],
        *,
        guild_id: str | None = None,
        timeout_sec: float,
    ) -> set[str]:
        deadline = time.monotonic() + timeout_sec
        last_names: set[str] = set()
        while time.monotonic() < deadline:
            last_names = await self.collect_command_names(guild_id=guild_id)
            if required.issubset(last_names):
                return last_names
            await asyncio.sleep(5)
        raise RuntimeError(
            f"Timed out waiting for application commands {sorted(required)}. "
            f"Last seen from API: {sorted(last_names)[:40]}"
        )

    async def wait_for_global_command_names(
        self,
        required: set[str],
        timeout_sec: float,
    ) -> None:
        await self.wait_for_application_command_names(
            required,
            timeout_sec=timeout_sec,
        )

    async def _list_channel_messages(self, channel_id: str, *, limit: int = 25) -> list[dict[str, Any]]:
        data = await self.request(
            "GET",
            f"/channels/{channel_id}/messages",
            params={"limit": str(limit)},
        )
        assert isinstance(data, list)
        return data

    async def bot_message_ids(self, channel_id: str, bot_user_id: str) -> set[str]:
        ids: set[str] = set()
        for message in await self._list_channel_messages(channel_id):
            author = message.get("author") or {}
            if str(author.get("id")) == bot_user_id:
                ids.add(str(message["id"]))
        return ids

    async def bot_embed_message_ids(self, channel_id: str, bot_user_id: str) -> set[str]:
        ids: set[str] = set()
        for message in await self._list_channel_messages(channel_id):
            author = message.get("author") or {}
            if str(author.get("id")) != bot_user_id:
                continue
            if message.get("embeds"):
                ids.add(str(message["id"]))
        return ids

    async def wait_for_new_bot_embed(
        self,
        channel_id: str,
        bot_user_id: str,
        *,
        exclude_message_ids: set[str],
        timeout_sec: float,
        poll_sec: float = 1.0,
    ) -> dict[str, Any]:
        result = await self.wait_for_new_bot_response(
            channel_id,
            bot_user_id,
            exclude_message_ids=exclude_message_ids,
            timeout_sec=timeout_sec,
            poll_sec=poll_sec,
            kind="embed",
        )
        embed = result.get("embed")
        assert embed is not None
        return embed

    async def wait_for_new_bot_response(
        self,
        channel_id: str,
        bot_user_id: str,
        *,
        exclude_message_ids: set[str],
        timeout_sec: float,
        poll_sec: float = 1.0,
        kind: str = "embed",
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() < deadline:
            for message in await self._list_channel_messages(channel_id):
                message_id = str(message.get("id", ""))
                if message_id in exclude_message_ids:
                    continue
                author = message.get("author") or {}
                if str(author.get("id")) != bot_user_id:
                    continue
                embeds = message.get("embeds") or []
                content = str(message.get("content") or "")
                has_embed = bool(embeds)
                has_content = bool(content.strip())
                if kind == "embed" and has_embed:
                    return {
                        "embed": embeds[0],
                        "content": content or None,
                        "message": message,
                    }
                if kind == "message" and has_content:
                    return {
                        "embed": embeds[0] if embeds else None,
                        "content": content,
                        "message": message,
                    }
                if kind == "any" and (has_embed or has_content):
                    return {
                        "embed": embeds[0] if embeds else None,
                        "content": content or None,
                        "message": message,
                    }
            await asyncio.sleep(poll_sec)
        recent = await self._list_channel_messages(channel_id, limit=10)
        summary = [
            {
                "id": msg.get("id"),
                "author": (msg.get("author") or {}).get("id"),
                "has_embeds": bool(msg.get("embeds")),
                "has_content": bool(str(msg.get("content") or "").strip()),
            }
            for msg in recent[:5]
        ]
        raise RuntimeError(
            f"Timed out waiting for new bot {kind} response. "
            f"Recent messages: {summary}"
        )
