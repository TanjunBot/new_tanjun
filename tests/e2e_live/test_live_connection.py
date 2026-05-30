import os

import pytest

pytestmark = pytest.mark.live_discord


@pytest.mark.asyncio
async def test_bot_token_configured() -> None:
    token = os.environ.get("TANJUN_TEST_BOT_TOKEN", "")
    assert len(token) > 20


@pytest.mark.asyncio
async def test_guild_id_configured() -> None:
    guild_id = os.environ.get("TANJUN_TEST_GUILD_ID", "")
    assert guild_id.isdigit()


@pytest.mark.asyncio
async def test_channel_id_configured() -> None:
    channel_id = os.environ.get("TANJUN_TEST_CHANNEL_ID", "")
    assert channel_id.isdigit()


@pytest.mark.asyncio
async def test_discord_api_reachable() -> None:
    token = os.environ.get("TANJUN_TEST_BOT_TOKEN", "")
    if not token:
        pytest.skip("TANJUN_TEST_BOT_TOKEN not set")
    import aiohttp

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://discord.com/api/v10/users/@me",
            headers={"Authorization": f"Bot {token}"},
            timeout=aiohttp.ClientTimeout(total=15),
        ) as resp:
            assert resp.status == 200

