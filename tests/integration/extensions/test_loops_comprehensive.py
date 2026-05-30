from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_guild, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.loops"
GUILD_ID = "123456789012345678"


def _identity_loop(**kwargs):
    def decorator(func):
        func.start = MagicMock()
        func.coro = func
        return func

    return decorator


@pytest.fixture
async def loop_cog():
    with patch("discord.ext.tasks.loop", _identity_loop):
        import extensions.loops as loops_mod

        importlib.reload(loops_mod)
        bot = await load_extension_bot(EXTENSION, fire_ready=False)
        cog = loops_mod.LoopCog(bot)
        yield cog, loops_mod, bot


class TestLogLoopError:
    def test_logs_without_sentry(self, loop_cog) -> None:
        _, loops_mod, _ = loop_cog
        with patch.object(loops_mod, "sentry_dsn", ""):
            loops_mod._log_loop_error("test_task")

    def test_logs_with_sentry(self, loop_cog) -> None:
        _, loops_mod, _ = loop_cog
        with (
            patch.object(loops_mod, "sentry_dsn", "https://example@sentry.io/1"),
            patch("sentry_sdk.capture_exception") as capture,
        ):
            loops_mod._log_loop_error("test_task")
            capture.assert_called_once()


@pytest.mark.parametrize(
    "loop_name,patch_target",
    [
        ("sendSendReadyGiveaways", "sendReadyGiveaways"),
        ("endGiveawaysLoop", "endGiveaways"),
        ("checkVoiceUsers", "checkVoiceUsers"),
        ("clearNotifiedUsersLoop", "clearNotifiedUsers"),
        ("addVoiceUserLoop", "addXpToVoiceUsers"),
        ("refillAiTokenLoop", "refill_ai_token"),
        ("pingServerLoop", "ping_server"),
        ("backupDatabaseLoop", "create_database_backup"),
        ("removeExpiredClaimedBoosterRoles", "remove_claimed_booster_roles_that_are_expired"),
        ("removeExpiredClaimedBoosterChannels", "remove_claimed_booster_channels_that_are_expired"),
        ("sendScheduledMessages", "send_scheduled_messages"),
    ],
)
async def test_loop_success_and_exception(loop_cog, loop_name: str, patch_target: str) -> None:
    cog, loops_mod, bot = loop_cog
    loop_fn = getattr(cog, loop_name)
    is_async = patch_target != "clearNotifiedUsers"
    mock = AsyncMock() if is_async else MagicMock()
    with patch.object(loops_mod, patch_target, new=mock) as mocked:
        await loop_fn()
        if is_async:
            mocked.assert_awaited_once_with(bot)
        else:
            mocked.assert_called_once_with(bot)
    fail_mock = (
        AsyncMock(side_effect=RuntimeError("loop fail")) if is_async else MagicMock(side_effect=RuntimeError("loop fail"))
    )
    with patch.object(loops_mod, patch_target, new=fail_mock):
        await loop_fn()


async def test_poll_twitch_no_service(loop_cog) -> None:
    cog, loops_mod, _ = loop_cog
    with patch.object(loops_mod, "get_twitch_service", return_value=None):
        await cog.pollTwitchStreams()


async def test_poll_twitch_no_uuids(loop_cog) -> None:
    cog, loops_mod, _ = loop_cog
    svc = MagicMock()
    svc.get_all_notification_uuids = AsyncMock(return_value=[])
    with patch.object(loops_mod, "get_twitch_service", return_value=svc):
        await cog.pollTwitchStreams()


async def test_poll_twitch_initial_check(loop_cog) -> None:
    cog, loops_mod, _ = loop_cog
    svc = MagicMock()
    svc.get_all_notification_uuids = AsyncMock(return_value=["uuid1"])
    svc.initial_check_done = False
    svc.initialize_stream_status = AsyncMock()
    with patch.object(loops_mod, "get_twitch_service", return_value=svc):
        await cog.pollTwitchStreams()
    svc.initialize_stream_status.assert_awaited_once()


async def test_poll_twitch_newly_live(loop_cog) -> None:
    cog, loops_mod, bot = loop_cog
    svc = MagicMock()
    svc.get_all_notification_uuids = AsyncMock(return_value=["user1"])
    svc.initial_check_done = True
    svc.stream_status = {"user1": False}
    svc.get_streams = AsyncMock(return_value=[{"user_id": "user1", "title": "live"}])
    with (
        patch.object(loops_mod, "get_twitch_service", return_value=svc),
        patch.object(loops_mod, "notify_twitch_online", new=AsyncMock()) as notify,
    ):
        await cog.pollTwitchStreams()
    notify.assert_awaited_once()


async def test_poll_twitch_exception(loop_cog) -> None:
    cog, loops_mod, _ = loop_cog
    with patch.object(loops_mod, "get_twitch_service", side_effect=RuntimeError("twitch fail")):
        await cog.pollTwitchStreams()


async def test_send_pokemon_werbung_publishes(loop_cog) -> None:
    cog, _, bot = loop_cog
    channel = make_text_channel()
    channel.send = AsyncMock(return_value=MagicMock(guild=make_guild(), publish=AsyncMock()))
    bot.get_channel = MagicMock(return_value=channel)
    await cog.sendPokemonWerbung()
    channel.send.assert_awaited_once()


async def test_send_pokemon_werbung_non_text_channel(loop_cog) -> None:
    cog, _, bot = loop_cog
    bot.get_channel = MagicMock(return_value=MagicMock())
    await cog.sendPokemonWerbung()


async def test_send_pokemon_werbung_exception(loop_cog) -> None:
    cog, _, bot = loop_cog
    channel = make_text_channel()
    channel.send = AsyncMock(side_effect=RuntimeError("send fail"))
    bot.get_channel = MagicMock(return_value=channel)
    await cog.sendPokemonWerbung()


async def test_on_ready_starts_all_loops(loop_cog) -> None:
    cog, _, bot = loop_cog
    bot._pool_ready = __import__("asyncio").Event()
    bot._pool_ready.set()
    await cog.on_ready()
    for name in (
        "pollTwitchStreams",
        "sendSendReadyGiveaways",
        "endGiveawaysLoop",
        "checkVoiceUsers",
        "clearNotifiedUsersLoop",
        "addVoiceUserLoop",
        "refillAiTokenLoop",
        "pingServerLoop",
        "backupDatabaseLoop",
        "removeExpiredClaimedBoosterRoles",
        "removeExpiredClaimedBoosterChannels",
        "sendScheduledMessages",
        "sendPokemonWerbung",
    ):
        assert getattr(cog, name).start.called
