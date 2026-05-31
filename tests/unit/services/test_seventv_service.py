from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.seventv_service import SevenTVEmote, SevenTVService, get_seventv_service


class TestSevenTVEmote:
    def test_from_api_data_static_png(self):
        emote = SevenTVEmote.from_api_data(
            {"id": "abc", "animated": False, "owner": {"display_name": "User"}, "tags": ["tag1"]},
            {"name": "Pepe", "data": {"id": "abc", "animated": False, "host": {"url": "//cdn.test", "files": [{"name": "4x.png"}]}}},
        )
        assert emote.name == "Pepe"
        assert emote.id == "abc"
        assert "4x.png" in emote.image_url

    def test_from_api_data_animated_gif(self):
        emote = SevenTVEmote.from_api_data(
            {"id": "xyz", "animated": True},
            {"name": "Dance", "data": {"id": "xyz", "animated": True, "host": {"url": "//cdn.test", "files": [{"name": "4x.gif"}]}}},
        )
        assert emote.animated is True
        assert emote.image_url.endswith("4x.gif")


    def test_from_api_data_webp_fallback(self):
        emote = SevenTVEmote.from_api_data(
            {"id": "abc"},
            {"name": "Fallback", "data": {"id": "abc", "animated": False, "host": {"url": "//cdn.test", "files": []}}},
        )
        assert emote.image_url.endswith("4x.webp")

    def test_from_api_data_cdn_fallback_without_host(self):
        emote = SevenTVEmote.from_api_data({"id": "abc"}, {"name": "NoHost", "data": {"id": "abc"}})
        assert "emote/abc" in emote.image_url


class TestSevenTVService:
    @pytest.mark.asyncio
    async def test_search_user_by_twitch_name_found(self):
        svc = SevenTVService()
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.json = AsyncMock(
            return_value={
                "data": {
                    "users": [
                        {
                            "id": "u1",
                            "username": "seven",
                            "display_name": "Seven",
                            "avatar_url": "https://cdn.test/a.png",
                            "connections": [
                                {
                                    "platform": "TWITCH",
                                    "username": "Streamer",
                                    "emote_set_id": "set1",
                                }
                            ],
                        }
                    ]
                }
            }
        )
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)
        emote_resp = AsyncMock()
        emote_resp.status = 200
        emote_resp.json = AsyncMock(
            return_value={
                "emote_set": {
                    "emotes": [
                        {
                            "name": "Pepe",
                            "data": {
                                "id": "e1",
                                "animated": False,
                                "host": {"url": "//cdn.test", "files": [{"name": "4x.png"}]},
                            },
                        }
                    ]
                }
            }
        )
        mock_session.get = AsyncMock(return_value=emote_resp)
        user = await svc._search_user_by_twitch_name(mock_session, "Streamer")
        assert user is not None
        assert user.username == "seven"
        assert len(user.emotes) == 1
        await svc.close()

    @pytest.mark.asyncio
    async def test_search_user_non_200_returns_none(self):
        svc = SevenTVService()
        mock_resp = AsyncMock(status=500)
        mock_session = AsyncMock()
        mock_session.post = AsyncMock(return_value=mock_resp)
        assert await svc._search_user_by_twitch_name(mock_session, "x") is None
        await svc.close()

    @pytest.mark.asyncio
    async def test_get_user_by_twitch_returns_none_on_error(self):
        svc = SevenTVService()
        with patch.object(svc, "_search_user_by_twitch_name", AsyncMock(side_effect=RuntimeError("network"))):
            result = await svc.get_user_by_twitch("streamer")
        assert result is None
        await svc.close()

    @pytest.mark.asyncio
    async def test_get_emote_image_bytes_success(self):
        svc = SevenTVService()
        mock_resp = AsyncMock()
        mock_resp.status = 200
        mock_resp.read = AsyncMock(return_value=b"png")
        mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_resp.__aexit__ = AsyncMock(return_value=None)
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        mock_session.closed = False
        svc._session = mock_session
        data = await svc.get_emote_image_bytes("https://cdn.test/emote.png")
        assert data == b"png"
        await svc.close()

    def test_get_seventv_service_singleton(self):
        a = get_seventv_service()
        b = get_seventv_service()
        assert a is b
