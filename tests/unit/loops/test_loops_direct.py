from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from loops import alivemonitor, create_database_backup, giveaway, level
from loops._voice_tracker import VoiceUserManager, voice_user_manager
from tests.helpers.discord import make_guild, make_member

pytestmark = pytest.mark.asyncio


async def test_ping_server_no_client():
    await alivemonitor.ping_server(None)


async def test_ping_server_no_user():
    client = MagicMock()
    client.user = None
    await alivemonitor.ping_server(client)


@patch("loops.alivemonitor.config.UPTIME_KUMA_PUSH_TOKEN", "")
async def test_ping_server_skipped_when_token_unset():
    client = MagicMock()
    client.user = MagicMock(id=1)
    client.latency = 0.1
    with patch("loops.alivemonitor.aiohttp.ClientSession") as mock_session_cls:
        await alivemonitor.ping_server(client)
        mock_session_cls.assert_not_called()


@patch("loops.alivemonitor.config.UPTIME_KUMA_STATUS_URL", "https://status.example.test")
@patch("loops.alivemonitor.config.UPTIME_KUMA_PUSH_TOKEN", "test-push-token")
@patch("loops.alivemonitor.aiohttp.ClientSession")
async def test_ping_server_push_success(mock_session_cls):
    client = MagicMock()
    client.user = MagicMock(id=1)
    client.latency = 0.1
    resp = AsyncMock()
    resp.status = 200
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    session = AsyncMock()
    session.get = MagicMock(return_value=resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mock_session_cls.return_value = session
    await alivemonitor.ping_server(client)
    call_url = session.get.call_args[0][0]
    assert "/api/push/test-push-token" in call_url
    assert "status=up" in call_url
    assert "ping=100" in call_url


@patch("loops.alivemonitor.config.UPTIME_KUMA_PUSH_TOKEN", "")
@patch("loops.alivemonitor.config.BOTSTATUS_API_URL", "https://botstatus-api.example.test/status")
@patch("loops.alivemonitor.aiohttp.ClientSession")
async def test_ping_server_botstatus_api_push(mock_session_cls):
    client = MagicMock()
    client.user = MagicMock(id=1)
    client.latency = 0.05
    client.guilds = [1, 2, 3]

    resp = AsyncMock()
    resp.status = 200
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    session = AsyncMock()
    session.post = MagicMock(return_value=resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mock_session_cls.return_value = session

    await alivemonitor.ping_server(client)
    session.post.assert_called_once()
    assert session.post.call_args[0][0] == "https://botstatus-api.example.test/status"
    payload = session.post.call_args[1]["json"]
    assert payload["id"] == "1"
    assert payload["status"] == "alive"
    assert payload["latency_ms"] == 50


@patch("loops.alivemonitor.config.UPTIME_KUMA_STATUS_URL", "https://status.example.test")
@patch("loops.alivemonitor.config.UPTIME_KUMA_PUSH_TOKEN", "test-push-token")
@patch("loops.alivemonitor.aiohttp.ClientSession")
async def test_ping_server_failure_status(mock_session_cls):
    client = MagicMock()
    client.user = MagicMock(id=1)
    client.latency = 0.1
    resp = AsyncMock()
    resp.status = 500
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    session = AsyncMock()
    session.get = MagicMock(return_value=resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mock_session_cls.return_value = session
    await alivemonitor.ping_server(client)


@patch("loops.alivemonitor.config.UPTIME_KUMA_STATUS_URL", "https://status.example.test")
@patch("loops.alivemonitor.config.UPTIME_KUMA_PUSH_TOKEN", "test-push-token")
@patch("loops.alivemonitor.aiohttp.ClientSession")
async def test_ping_server_infinite_latency_uses_zero(mock_session_cls):
    client = MagicMock()
    client.user = MagicMock(id=1)
    client.latency = float("inf")
    resp = AsyncMock()
    resp.status = 200
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    session = AsyncMock()
    session.get = MagicMock(return_value=resp)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    mock_session_cls.return_value = session
    await alivemonitor.ping_server(client)
    call_url = session.get.call_args[0][0]
    assert "ping=0" in call_url


@patch("loops.create_database_backup.database_password", "pw")
@patch("loops.create_database_backup.database_user", "user")
@patch("loops.create_database_backup.dump_database_schema", new_callable=AsyncMock)
async def test_create_database_backup_success(mock_dump, *_):
    client = MagicMock()
    channel = MagicMock()
    channel.send = AsyncMock()
    client.get_channel = MagicMock(return_value=channel)
    await create_database_backup.create_database_backup(client)
    mock_dump.assert_awaited_once()


@patch("loops.create_database_backup.dump_database_schema", new_callable=AsyncMock, side_effect=RuntimeError("fail"))
async def test_create_database_backup_dump_error(mock_dump):
    client = MagicMock()
    client.get_channel = MagicMock(return_value=None)
    with pytest.raises(RuntimeError):
        await create_database_backup.create_database_backup(client)


@patch("loops.giveaway.sendGiveaway", new_callable=AsyncMock)
@patch("loops.giveaway.giveaway_service.get_send_ready", new_callable=AsyncMock, return_value=[1, 2])
async def test_send_ready_giveaways(mock_ready, mock_send):
    await giveaway.sendReadyGiveaways(MagicMock())
    assert mock_send.await_count == 2


@patch("loops.giveaway.giveaway_service.add_voice_minutes", new_callable=AsyncMock)
async def test_check_voice_users(mock_add):
    voice_user_manager.clear()
    voice_user_manager.add(1, 2)
    await giveaway.checkVoiceUsers(MagicMock())
    mock_add.assert_awaited_once()
    voice_user_manager.clear()


@patch("loops.giveaway.endGiveaway", new_callable=AsyncMock)
@patch("loops.giveaway.giveaway_service.get_end_ready", new_callable=AsyncMock, return_value=[3])
async def test_end_giveaways(mock_ready, mock_end):
    await giveaway.endGiveaways(MagicMock())
    mock_end.assert_awaited_once()


@patch("loops.level.update_user_xp_from_voice", new_callable=AsyncMock)
@patch("loops.level.fetch_xp_details", new_callable=AsyncMock, return_value=10)
@patch("loops.level.is_entity_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("loops.level.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_add_xp_to_voice_users(mock_status, mock_blacklist, mock_xp, mock_update):
    guild = make_guild()
    member = make_member()
    member.voice = MagicMock()
    member.voice.channel = MagicMock(id=99)
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    voice_user_manager.clear()
    voice_user_manager.add(int(member.id), int(guild.id))
    await level.addXpToVoiceUsers(client)
    mock_update.assert_awaited_once()
    voice_user_manager.clear()


@patch("loops.level.get_level_system_status", new_callable=AsyncMock, return_value=False)
async def test_add_xp_disabled_system(mock_status):
    guild = make_guild()
    member = make_member()
    guild.get_member = MagicMock(return_value=member)
    client = MagicMock()
    client.get_guild = MagicMock(return_value=guild)
    voice_user_manager.clear()
    voice_user_manager.add(int(member.id), int(guild.id))
    await level.addXpToVoiceUsers(client)
    voice_user_manager.clear()


async def test_voice_user_manager_track_and_clear() -> None:
    mgr = VoiceUserManager()
    mgr.add(1, 2)
    assert mgr.get_active_users() == [(1, 2)]
    mgr.remove(1, 2)
    mgr.clear()
    assert mgr.get_active_users() == []
