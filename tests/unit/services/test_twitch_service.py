"""Tests for services/twitch_service.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import discord
import pytest

from models import TwitchUserModel
from services import twitch_service as twitch_module
from services.twitch_service import (
    LiveStreamInfo,
    TwitchNotification,
    TwitchService,
    get_twitch_service,
    init_twitch_service,
)
from tests.helpers.discord import make_guild, make_text_channel
from tests.helpers.factories import CHANNEL_ID, GUILD_ID


def _mock_resp(json_data: dict | None = None, status: int = 200):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


def _notification_row(
    notification_id: str = "1",
    message: str | None = "Hello {name}",
):
    return (notification_id, CHANNEL_ID, GUILD_ID, "uuid123456789012345", "streamer", message)


@pytest.fixture
def service() -> TwitchService:
    svc = TwitchService()
    svc.client_id = "mock_twitch_id_123"
    svc.client_secret = "mock_twitch_secret"
    svc.access_token = "mock_token"
    svc.headers = {"Client-ID": "mock_twitch_id_123", "Authorization": "Bearer mock_token"}
    return svc


@pytest.fixture(autouse=True)
def _reset_singleton():
    twitch_module._twitch_service = None
    yield
    twitch_module._twitch_service = None


class TestLiveStreamInfo:
    def test_from_api_data_full(self):
        data = {
            "user_id": "123",
            "user_name": "streamer",
            "title": "Live now",
            "viewer_count": 500,
            "started_at": "2024-01-01T00:00:00Z",
            "thumbnail_url": "https://example.com/{width}x{height}.jpg",
        }
        info = LiveStreamInfo.from_api_data(data)
        assert info.user_id == "123"
        assert info.user_name == "streamer"
        assert info.title == "Live now"
        assert info.viewer_count == 500

    def test_from_api_data_defaults(self):
        info = LiveStreamInfo.from_api_data({})
        assert info.user_id == ""
        assert info.viewer_count == 0


class TestTwitchNotification:
    def test_dataclass_fields(self):
        n = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", "msg")
        assert n.twitch_name == "name"
        assert n.notification_message == "msg"


class TestTwitchServiceInit:
    @pytest.mark.asyncio
    async def test_init_sets_session_and_token(self, service: TwitchService):
        token_resp = _mock_resp({"access_token": "tok123"})
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=token_resp)
        mock_session.close = AsyncMock()
        service.client_id = "client-id"
        service.client_secret = "secret"

        with patch("services.twitch_service.aiohttp.ClientSession", return_value=mock_session):
            await service.init()

        assert service.session is mock_session
        assert service.access_token == "tok123"
        assert service.headers is not None
        assert service.headers["Client-ID"] == "client-id"

    @pytest.mark.asyncio
    async def test_init_without_credentials(self, service: TwitchService):
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = MagicMock()
        service.client_id = None
        service.client_secret = None
        service.access_token = None
        service.headers = None
        with patch("services.twitch_service.aiohttp.ClientSession", return_value=mock_session):
            await service.init()
        assert service.access_token is None
        mock_session.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_init_token_network_error(self, service: TwitchService):
        mock_session = AsyncMock()
        mock_session.post = MagicMock(side_effect=aiohttp.ClientError("fail"))
        service.client_id = "id"
        service.client_secret = "secret"
        with patch("services.twitch_service.aiohttp.ClientSession", return_value=mock_session):
            await service.init()
        assert service.access_token is None

    @pytest.mark.asyncio
    async def test_init_token_unexpected_error(self, service: TwitchService):
        mock_session = AsyncMock()
        mock_session.post = MagicMock(side_effect=RuntimeError("boom"))
        service.client_id = "id"
        service.client_secret = "secret"
        with patch("services.twitch_service.aiohttp.ClientSession", return_value=mock_session):
            await service.init()
        assert service.access_token is None

    @pytest.mark.asyncio
    async def test_close(self, service: TwitchService):
        mock_session = AsyncMock()
        service.session = mock_session
        await service.close()
        mock_session.close.assert_awaited_once()
        assert service.session is None

    @pytest.mark.asyncio
    async def test_setup_headers_without_token(self, service: TwitchService):
        service.client_id = "id"
        service.client_secret = "secret"
        service.access_token = None
        await service._setup_headers()
        assert service.headers is None


class TestTwitchServiceApi:
    @pytest.mark.asyncio
    async def test_get_user_by_login_no_session(self, service: TwitchService):
        service.client_id = None
        service.client_secret = None
        assert await service.get_user_by_login("streamer") is None

    @pytest.mark.asyncio
    async def test_get_user_by_login_found(self, service: TwitchService):
        user_data = {"id": "1", "login": "streamer", "display_name": "Streamer"}
        api_resp = _mock_resp({"data": [user_data]})
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(return_value=api_resp)
        service.session = mock_session
        service.access_token = "tok"
        service.headers = {"Client-ID": "cid", "Authorization": "Bearer tok"}

        result = await service.get_user_by_login("streamer")
        assert isinstance(result, TwitchUserModel)
        assert result.login == "streamer"

    @pytest.mark.asyncio
    async def test_get_user_by_login_not_found(self, service: TwitchService):
        api_resp = _mock_resp({"data": []})
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(return_value=api_resp)
        service.session = mock_session
        service.access_token = "tok"
        service.headers = {"Client-ID": "cid", "Authorization": "Bearer tok"}

        assert await service.get_user_by_login("missing") is None

    @pytest.mark.asyncio
    async def test_get_user_by_login_401_retries_with_new_token(self, service: TwitchService):
        user_data = {"id": "1", "login": "streamer", "display_name": "Streamer"}
        resp_401 = _mock_resp({"error": "Unauthorized"}, status=401)
        resp_200 = _mock_resp({"data": [user_data]}, status=200)
        token_resp = _mock_resp({"access_token": "new-tok"}, status=200)

        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(side_effect=[resp_401, resp_200])
        mock_session.post = MagicMock(return_value=token_resp)
        service.session = mock_session
        service.client_id = "cid"
        service.client_secret = "csec"
        service.access_token = "old-tok"
        service.headers = {"Client-ID": "cid", "Authorization": "Bearer old-tok"}

        result = await service.get_user_by_login("streamer")
        assert isinstance(result, TwitchUserModel)
        assert result.login == "streamer"
        assert service.access_token == "new-tok"

    @pytest.mark.asyncio
    async def test_get_streams_empty_user_ids(self, service: TwitchService):
        assert await service.get_streams([]) == []

    @pytest.mark.asyncio
    async def test_get_streams_success(self, service: TwitchService):
        stream_data = {
            "user_id": "123",
            "user_name": "s",
            "title": "t",
            "viewer_count": 10,
            "started_at": "now",
            "thumbnail_url": "url",
        }
        api_resp = _mock_resp({"data": [stream_data]})
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(return_value=api_resp)
        service.session = mock_session
        service.access_token = "tok"
        service.headers = {"Client-ID": "cid", "Authorization": "Bearer tok"}

        streams = await service.get_streams(["123"])
        assert streams is not None
        assert len(streams) == 1
        assert streams[0].user_id == "123"

    @pytest.mark.asyncio
    async def test_get_streams_chunking(self, service: TwitchService):
        stream_data = {
            "user_id": "123",
            "user_name": "s",
            "title": "t",
            "viewer_count": 10,
            "started_at": "now",
            "thumbnail_url": "url",
        }
        api_resp1 = _mock_resp({"data": [stream_data]})
        api_resp2 = _mock_resp({"data": []})
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.request = MagicMock(side_effect=[api_resp1, api_resp2])
        service.session = mock_session
        service.access_token = "tok"
        service.headers = {"Client-ID": "cid", "Authorization": "Bearer tok"}

        user_ids = [str(i) for i in range(150)]
        streams = await service.get_streams(user_ids)
        assert streams is not None
        assert len(streams) == 1
        assert mock_session.request.call_count == 2

    @pytest.mark.asyncio
    async def test_get_streams_network_error(self, service: TwitchService):
        mock_session = AsyncMock()
        mock_session.request = MagicMock(side_effect=aiohttp.ClientError("fail"))
        service.session = mock_session
        service.headers = {}
        assert await service.get_streams(["123"]) is None

    @pytest.mark.asyncio
    async def test_initialize_stream_status(self, service: TwitchService):
        stream = LiveStreamInfo("a", "n", "t", 1, "s", "u")
        with patch.object(service, "get_streams", new_callable=AsyncMock) as mock_streams:
            mock_streams.return_value = [stream]
            await service.initialize_stream_status(["a", "b"])
        assert service.stream_status["a"] is True
        assert service.stream_status["b"] is False
        assert service.initial_check_done is True

    @pytest.mark.asyncio
    async def test_initialize_stream_status_empty(self, service: TwitchService):
        with patch.object(service, "get_streams", new_callable=AsyncMock) as mock_streams:
            await service.initialize_stream_status([])
        mock_streams.assert_not_awaited()


class TestTwitchServiceNotifications:
    @pytest.mark.asyncio
    async def test_get_notifications(self, service: TwitchService):
        async def fake_iter(*args, **kwargs):
            yield _notification_row()

        with patch("services.twitch_service.execute_query_iter", side_effect=fake_iter):
            result = await service.get_notifications(CHANNEL_ID)
        assert len(result) == 1
        assert result[0].twitch_name == "streamer"

    @pytest.mark.asyncio
    async def test_add_notification(self, service: TwitchService):
        with patch("services.twitch_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.add_notification(GUILD_ID, CHANNEL_ID, "uuid", "name", "msg")
            assert "INSERT INTO twitchOnlineNotification" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_remove_notification(self, service: TwitchService):
        with patch("services.twitch_service.execute_action", new_callable=AsyncMock) as mock_exec:
            await service.remove_notification("5")
            assert "DELETE FROM twitchOnlineNotification" in mock_exec.await_args[0][0]

    @pytest.mark.asyncio
    async def test_get_notification_by_twitch_uuid(self, service: TwitchService):
        with patch("services.twitch_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = [_notification_row()]
            result = await service.get_notification_by_twitch_uuid("uuid123456789012345")
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_notification_by_twitch_uuid_empty(self, service: TwitchService):
        with patch("services.twitch_service.safe_execute_query", new_callable=AsyncMock) as mock_q:
            mock_q.return_value = None
            result = await service.get_notification_by_twitch_uuid("missing")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_all_notification_uuids(self, service: TwitchService):
        async def fake_iter(*args, **kwargs):
            yield ("uuid-1",)
            yield ("uuid-2",)

        with patch("services.twitch_service.execute_query_iter", side_effect=fake_iter):
            result = await service.get_all_notification_uuids()
        assert result == ["uuid-1", "uuid-2"]

    @pytest.mark.asyncio
    async def test_get_notifications_by_guild(self, service: TwitchService):
        async def fake_iter(*args, **kwargs):
            yield _notification_row()

        with patch("services.twitch_service.execute_query_iter", side_effect=fake_iter):
            result = await service.get_notifications_by_guild(GUILD_ID)
        assert len(result) == 1


class TestTwitchServiceParseNotification:
    def test_custom_message_replaces_name(self, service: TwitchService):
        result = service.parse_notification_message("Go watch {name}!", "en-US", "Streamer")
        assert result == "Go watch Streamer!"

    def test_default_message_when_none(self, service: TwitchService):
        import services.twitch_service as twitch_mod
        # _locale is a frozen dataclass; replace the module-level reference instead
        orig = twitch_mod._locale
        mock_locale = MagicMock()
        mock_locale.commands.utility.twitch.defaultNotificationMessage = MagicMock(return_value="Default {name} live")
        twitch_mod._locale = mock_locale
        try:
            result = service.parse_notification_message(None, "en-US", "Streamer")
        finally:
            twitch_mod._locale = orig
        assert result == "Default Streamer live"


class TestTwitchServiceSendLiveNotification:
    @pytest.fixture(autouse=True)
    def _patch_discord_channel_types(self):
        import services.twitch_service as mod

        class ForumChannel:
            pass

        class CategoryChannel:
            pass

        with patch.object(mod.discord, "ForumChannel", ForumChannel):
            with patch.object(mod.discord, "CategoryChannel", CategoryChannel):
                yield

    @pytest.mark.asyncio
    async def test_send_no_notifications(self, service: TwitchService):
        client = MagicMock()
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []
            await service.send_live_notification(client, "uuid", LiveStreamInfo("uuid", "s", "t", 0, "", "u"))
        client.get_guild.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_skips_missing_guild(self, service: TwitchService):
        client = MagicMock()
        client.get_guild.return_value = None
        notification = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", None)
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [notification]
            await service.send_live_notification(
                client, "uuid", LiveStreamInfo("uuid", "s", "t", 0, "", "https://x/{width}/{height}")
            )

    @pytest.mark.asyncio
    async def test_send_to_channel(self, service: TwitchService):
        guild = make_guild(guild_id=int(GUILD_ID))
        channel = make_text_channel(channel_id=int(CHANNEL_ID), guild=guild)
        guild.get_channel = MagicMock(return_value=channel)
        client = MagicMock()
        client.get_guild.return_value = guild
        notification = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", "Watch {name}")
        stream_data = LiveStreamInfo("uuid", "streamer", "Playing games", 0, "", "https://x/{width}x{height}.jpg")
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [notification]
            await service.send_live_notification(client, "uuid", stream_data)
        channel.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_skips_forum_channel(self, service: TwitchService):
        import services.twitch_service as mod

        guild = make_guild(guild_id=int(GUILD_ID))
        forum = mod.discord.ForumChannel()
        guild.get_channel = MagicMock(return_value=forum)
        client = MagicMock()
        client.get_guild.return_value = guild
        notification = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", None)
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [notification]
            await service.send_live_notification(client, "uuid", LiveStreamInfo("uuid", "s", "t", 0, "", "u"))

    @pytest.mark.asyncio
    async def test_send_fallback_fetch_channel(self, service: TwitchService):
        guild = make_guild(guild_id=int(GUILD_ID))
        guild.get_channel = MagicMock(return_value=None)
        guild.get_thread = MagicMock(return_value=None)
        channel = make_text_channel(channel_id=int(CHANNEL_ID), guild=guild)
        client = MagicMock()
        client.get_guild.return_value = guild
        client.get_channel.return_value = None
        client.fetch_channel = AsyncMock(return_value=channel)

        notification = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", "Watch {name}")
        stream_data = LiveStreamInfo("uuid", "streamer", "Playing games", 0, "", "https://x/{width}x{height}.jpg")
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [notification]
            await service.send_live_notification(client, "uuid", stream_data)
        client.fetch_channel.assert_awaited_once_with(int(CHANNEL_ID))
        channel.send.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_send_handles_forbidden_error_gracefully(self, service: TwitchService):
        guild = make_guild(guild_id=int(GUILD_ID))
        channel = make_text_channel(channel_id=int(CHANNEL_ID), guild=guild)
        channel.send = AsyncMock(side_effect=discord.Forbidden(MagicMock(), "missing perms"))
        guild.get_channel = MagicMock(return_value=channel)
        client = MagicMock()
        client.get_guild.return_value = guild

        notification = TwitchNotification("1", CHANNEL_ID, GUILD_ID, "uuid", "name", "Watch {name}")
        stream_data = LiveStreamInfo("uuid", "streamer", "Playing games", 0, "", "https://x/{width}x{height}.jpg")
        with patch.object(service, "get_notification_by_twitch_uuid", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = [notification]
            # Should not raise exception
            await service.send_live_notification(client, "uuid", stream_data)


class TestTwitchServiceSingleton:
    @pytest.mark.asyncio
    async def test_init_twitch_service(self):
        mock_svc = AsyncMock()
        mock_svc.init = AsyncMock()
        mock_svc.close = AsyncMock()
        with patch("services.twitch_service.TwitchService", return_value=mock_svc):
            result = await init_twitch_service()
        assert result is mock_svc
        mock_svc.init.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_init_twitch_service_closes_existing(self):
        old = AsyncMock()
        old.close = AsyncMock()
        twitch_module._twitch_service = old
        new_svc = AsyncMock()
        new_svc.init = AsyncMock()
        with patch("services.twitch_service.TwitchService", return_value=new_svc):
            await init_twitch_service()
        old.close.assert_awaited_once()

    def test_get_twitch_service_none(self):
        assert get_twitch_service() is None

    def test_get_twitch_service_returns_instance(self):
        svc = TwitchService()
        twitch_module._twitch_service = svc
        assert get_twitch_service() is svc
