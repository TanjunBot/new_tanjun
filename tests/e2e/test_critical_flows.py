"""Critical end-to-end flows: counting, giveaway lifecycle, level XP."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_guild, make_member, make_message
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID, giveaway_row

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


async def test_counting_message_flow():
    config = {"progress": 0, "last_counter_id": None, "guild_id": GUILD_ID}
    msg = make_message(content="1", guild=make_guild(guild_id=int(GUILD_ID)))
    with patch("minigames._counting_common.counting", new=AsyncMock()) as base_counting:
        from minigames.counting import counting

        await counting(msg, config=config)
    base_counting.assert_awaited_once()


async def test_giveaway_lifecycle_flow():
    end = datetime.now(UTC) + timedelta(days=1)
    start = datetime.now(UTC)
    mock_model = MagicMock()
    mock_model.id = 1
    mock_model.guild_id = GUILD_ID
    with patch("services.giveaway_service.giveaway_service") as svc:
        svc.create = AsyncMock(return_value=1)
        svc.get = AsyncMock(return_value=mock_model)
        svc.set_started = AsyncMock()
        svc.set_ended = AsyncMock()
        from api import add_giveaway, get_giveaway, set_giveaway_ended, set_giveaway_started

        gid = await add_giveaway(
            guild_id=GUILD_ID,
            title="Prize",
            description="Win stuff",
            winners=1,
            with_button=True,
            channel_id=CHANNEL_ID,
            custom_name=None,
            sponsor=None,
            price=None,
            message=None,
            endtime=end,
            starttime=start,
            new_message_requirement=None,
            day_requirement=None,
            channel_requirements={},
            role_requirement=[],
            voice_requirement=None,
        )
        assert gid == 1
        assert await get_giveaway(1) is mock_model
        await set_giveaway_started(1)
        await set_giveaway_ended(1)
        svc.set_started.assert_awaited_once()
        svc.set_ended.assert_awaited_once()


async def test_level_xp_award_flow():
    guild = make_guild(guild_id=int(GUILD_ID))
    author = make_member(user_id=int(USER_ID))
    author.roles = []
    msg = make_message(content="hello world", author=author, guild=guild)
    with (
        patch("api.check_if_opted_out", new=AsyncMock(return_value=False)),
        patch("api.get_level_system_status", new=AsyncMock(return_value=True)),
        patch("minigames._xp_core.is_entity_blacklisted", new=AsyncMock(return_value=False)),
        patch("minigames.add_level_xp.fetch_xp_details", new=AsyncMock(return_value=("medium", None, 15))),
        patch("api.get_user_xp", new=AsyncMock(return_value=0)),
        patch("utility.get_level_for_xp_async", new=AsyncMock(return_value=1)),
        patch("minigames.add_level_xp.update_user_xp", new=AsyncMock()) as update_mock,
        patch("minigames.add_level_xp.handle_level_up", new=AsyncMock()),
    ):
        from minigames.add_level_xp import addLevelXp

        await addLevelXp(msg)
    update_mock.assert_awaited_once()


def test_giveaway_model_roundtrip():
    from models import GiveawayModel

    model = GiveawayModel.from_row(giveaway_row())
    assert model.title == "Test Giveaway"
    assert model.guild_id == GUILD_ID
