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
