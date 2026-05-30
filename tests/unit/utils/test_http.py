"""Tests for utils/http.py HTTP utilities with mocked aiohttp."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utils.http import getGif, upload_image_to_imgbb, upload_to_tanjun_logs


def _mock_response(status: int, json_data: dict | None = None, text: str = ""):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    resp.text = AsyncMock(return_value=text)
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


def _mock_session(get_response=None, post_response=None):
    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    if get_response is not None:
        session.get = MagicMock(return_value=get_response)
    if post_response is not None:
        session.post = MagicMock(return_value=post_response)
    return session


class TestGetGif:
    @pytest.mark.asyncio
    async def test_returns_urls_on_success(self):
        giphy_data = {"data": [{"images": {"downsized_medium": {"url": f"https://giphy.com/{i}.gif"}}} for i in range(3)]}
        mock_resp = _mock_response(200, giphy_data)
        mock_session = _mock_session(get_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            urls = await getGif("cat", amount=2)

        assert len(urls) == 2
        assert all("giphy.com" in u for u in urls)

    @pytest.mark.asyncio
    async def test_returns_empty_on_non_200(self):
        mock_resp = _mock_response(500)
        mock_session = _mock_session(get_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            urls = await getGif("cat")

        assert urls == []

    @pytest.mark.asyncio
    async def test_returns_empty_on_exception(self):
        with patch("utils.http.aiohttp.ClientSession", side_effect=TimeoutError):
            urls = await getGif("cat")
        assert urls == []


class TestUploadImageToImgbb:
    @pytest.mark.asyncio
    async def test_upload_returns_json(self):
        mock_resp = _mock_response(200, {"success": True, "data": {"url": "https://imgbb.com/x"}})
        mock_session = _mock_session(post_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            result = await upload_image_to_imgbb(b"fake_image", "png")

        assert result["success"] is True


class TestUploadToTanjunLogs:
    @pytest.mark.asyncio
    async def test_success_returns_url(self):
        mock_resp = _mock_response(201, {"key": "abc123"})
        mock_session = _mock_session(post_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            url = await upload_to_tanjun_logs("<html>test</html>")

        assert url == "https://mock.bytebin.url/abc123"

    @pytest.mark.asyncio
    async def test_missing_key_returns_none(self):
        mock_resp = _mock_response(201, {})
        mock_session = _mock_session(post_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            url = await upload_to_tanjun_logs("content")

        assert url is None

    @pytest.mark.asyncio
    async def test_non_201_returns_none(self):
        mock_resp = _mock_response(500, text="error")
        mock_session = _mock_session(post_response=mock_resp)

        with patch("utils.http.aiohttp.ClientSession", return_value=mock_session):
            url = await upload_to_tanjun_logs("content")

        assert url is None
