from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.live_discord, pytest.mark.asyncio]


@pytest.mark.skipif(
    not os.environ.get("TANJUN_TEST_BOT_TOKEN"),
    reason="Live token required",
)
async def test_fetch_application_info(live_bot_token: str):
    import aiohttp

    async with (
        aiohttp.ClientSession() as session,
        session.get(
            "https://discord.com/api/v10/oauth2/applications/@me",
            headers={"Authorization": f"Bot {live_bot_token}"},
        ) as resp,
    ):
        assert resp.status in (200, 401, 403)
        if resp.status == 200:
            data = await resp.json()
            assert "id" in data
