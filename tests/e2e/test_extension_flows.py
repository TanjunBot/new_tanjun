from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.e2e.conftest import load_extension_bot
from tests.helpers.discord import make_guild, make_interaction, make_member, make_message
from tests.helpers.factories import CHANNEL_ID, GUILD_ID, USER_ID, giveaway_row

pytestmark = [pytest.mark.asyncio, pytest.mark.e2e]


async def test_on_message_runs_handlers(listener_cog):
    msg = make_message(content="5", guild=make_guild(guild_id=int(GUILD_ID)))
    msg.author = make_member()
    msg.author.bot = False
    with (
        patch("extensions.listeners.get_counting_configs", new=AsyncMock(return_value=(None, None, None))),
        patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq_mock,
        patch("extensions.listeners.run_handlers_safe", new=AsyncMock()) as safe_mock,
    ):
        await listener_cog.on_message(msg)
    seq_mock.assert_awaited_once()
    safe_mock.assert_awaited_once()


async def test_on_message_with_counting_config(listener_cog):
    msg = make_message(content="1", guild=make_guild(guild_id=int(GUILD_ID)))
    msg.author = make_member()
    msg.author.bot = False
    config = {"progress": 0, "last_counter_id": None, "guild_id": str(GUILD_ID)}
    with (
        patch("extensions.listeners.get_counting_configs", new=AsyncMock(return_value=(config, None, None))),
        patch("extensions.listeners.run_handlers_sequential", new=AsyncMock()) as seq_mock,
    ):
        await listener_cog.on_message(msg)
    seq_mock.assert_awaited_once()
    handlers = seq_mock.call_args[0][0]
    assert any(h[0] == "counting" for h in handlers)


async def test_on_interaction_ignores_missing_data(listener_cog):
    interaction = make_interaction()
    interaction.data = None
    await listener_cog.on_interaction(interaction)


async def test_on_interaction_giveaway_button(listener_cog):
    interaction = make_interaction()
    interaction.data = {"custom_id": "giveaway_enter; 42"}
    with patch("extensions.listeners.add_giveaway_participant", new=AsyncMock(return_value=None)):
        await listener_cog.on_interaction(interaction)


async def test_on_member_join(listener_cog):
    member = make_member()
    with patch("extensions.listeners.welcomeNewUser", new=AsyncMock()) as welcome_mock:
        await listener_cog.on_member_join(member)
    welcome_mock.assert_awaited_once_with(member)


async def test_on_member_remove(listener_cog):
    member = make_member()
    with patch("extensions.listeners.farewellUser", new=AsyncMock()) as farewell_mock:
        await listener_cog.on_member_remove(member)
    farewell_mock.assert_awaited_once_with(member)


async def test_listener_skips_bot_messages():
    from extensions.listeners import ListenerCog

    bot = MagicMock()
    cog = ListenerCog(bot)
    msg = make_message()
    msg.author.bot = True
    with patch("extensions.listeners.get_counting_configs", new=AsyncMock()) as mock_configs:
        await cog.on_message(msg)
    mock_configs.assert_not_awaited()


async def test_listener_skips_dm_messages():
    from extensions.listeners import ListenerCog

    bot = MagicMock()
    cog = ListenerCog(bot)
    msg = make_message()
    msg.guild = None
    with patch("extensions.listeners.get_counting_configs", new=AsyncMock()) as mock_configs:
        await cog.on_message(msg)
    mock_configs.assert_not_awaited()


async def test_counting_handler_invokes_base_with_config():
    config = {"progress": 0, "last_counter_id": None, "guild_id": GUILD_ID}
    msg = make_message(content="1", guild=make_guild(guild_id=int(GUILD_ID)))
    with patch("minigames._counting_common.counting", new=AsyncMock()) as base_counting:
        from minigames.counting import counting

        await counting(msg, config=config)
    base_counting.assert_awaited_once()


async def test_add_level_xp_skips_opted_out():
    guild = make_guild(guild_id=int(GUILD_ID))
    author = make_member(user_id=int(USER_ID))
    author.roles = []
    msg = make_message(content="hello world", author=author, guild=guild)
    with (
        patch("api.check_if_opted_out", new=AsyncMock(return_value=True)),
        patch("api.get_level_system_status", new=AsyncMock()) as status_mock,
    ):
        from minigames.add_level_xp import addLevelXp

        await addLevelXp(msg)
    status_mock.assert_not_awaited()


async def test_add_level_xp_updates_xp_when_enabled():
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


def _giveaway_params():
    end = datetime.now(UTC) + timedelta(days=1)
    start = datetime.now(UTC)
    return dict(
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


async def test_giveaway_create_get_end_flow():
    mock_model = MagicMock()
    mock_model.id = 1
    mock_model.guild_id = GUILD_ID
    with patch("services.giveaway_service.giveaway_service") as svc:
        svc.create = AsyncMock(return_value=1)
        svc.get = AsyncMock(return_value=mock_model)
        svc.set_started = AsyncMock()
        svc.set_ended = AsyncMock()
        from api import add_giveaway, get_giveaway, set_giveaway_ended, set_giveaway_started

        gid = await add_giveaway(**_giveaway_params())
        assert gid == 1
        gw = await get_giveaway(1)
        assert gw is mock_model
        await set_giveaway_started(1)
        await set_giveaway_ended(1)
        svc.set_started.assert_awaited_once()
        svc.set_ended.assert_awaited_once()


async def test_giveaway_model_from_row():
    from models import GiveawayModel

    model = GiveawayModel.from_row(giveaway_row())
    assert model.title == "Test Giveaway"
    assert model.guild_id == GUILD_ID


async def test_loops_on_ready_starts_background_tasks():
    bot = await load_extension_bot("extensions.loops")
    cog = bot.cogs["LoopCog"]
    assert cog.pollTwitchStreams.start.called
    assert cog.endGiveawaysLoop.start.called


async def test_level_extension_exposes_level_cog():
    bot = await load_extension_bot("extensions.level", fire_ready=False)
    assert "levelCog" in bot.cogs


async def test_minigames_extension_exposes_minigame_cog():
    bot = await load_extension_bot("extensions.minigames", fire_ready=False)
    assert "MinigameCog" in bot.cogs
