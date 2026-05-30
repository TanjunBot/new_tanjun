"""Tests for services/external_api_client.py."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from services.external_api_client import ExternalApiClient, GiphyResponse, ImgBBResponse


@pytest.fixture
def client() -> ExternalApiClient:
    return ExternalApiClient(
        imgbb_key="test_imgbb",
        giphy_key="test_giphy",
        github_token="test_github",
        bytebin_url="https://bytebin.test",
        bytebin_username="user",
        bytebin_password="pass",
    )


def _mock_resp(status: int, json_data: dict | None = None):
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=json_data or {})
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=None)
    return resp


class TestExternalApiClient:
    @pytest.mark.asyncio
    async def test_get_session_creates_once(self, client: ExternalApiClient):
        mock_session = AsyncMock()
        mock_session.closed = False
        with patch("aiohttp.ClientSession", return_value=mock_session) as mock_cls:
            s1 = await client.get_session()
            s2 = await client.get_session()
            assert s1 is s2
            mock_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_to_imgbb_success(self, client: ExternalApiClient):
        mock_resp = _mock_resp(200, {"success": True, "data": {"url": "https://imgbb.com/x"}})
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            result = await client.upload_to_imgbb(b"data", "png")
        assert isinstance(result, ImgBBResponse)

    @pytest.mark.asyncio
    async def test_search_giphy_success(self, client: ExternalApiClient):
        mock_resp = _mock_resp(200, {"data": []})
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            result = await client.search_giphy("cat")
        assert isinstance(result, GiphyResponse)

    @pytest.mark.asyncio
    async def test_upload_to_bytebin_success(self, client: ExternalApiClient):
        mock_resp = _mock_resp(201, {"key": "abc123"})
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            url = await client.upload_to_bytebin("content")
        assert url == "https://bytebin.test/abc123"

    @pytest.mark.asyncio
    async def test_upload_to_bytebin_failure(self, client: ExternalApiClient):
        mock_resp = _mock_resp(500)
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            url = await client.upload_to_bytebin("content")
        assert url is None

    def test_create_github_issue(self, client: ExternalApiClient):
        mock_repo = MagicMock()
        mock_repo.get_label.return_value = MagicMock()
        mock_g = MagicMock()
        mock_g.get_repo.return_value = mock_repo
        with patch("services.external_api_client.Github", return_value=mock_g):
            client.create_github_issue("Title", "Body", ["bug"])
        mock_repo.create_issue.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, client: ExternalApiClient):
        mock_session = AsyncMock()
        mock_session.closed = False
        client._session = mock_session
        await client.close()
        mock_session.close.assert_awaited_once()
        assert client._session is None

    @pytest.mark.asyncio
    async def test_upload_imgbb_no_key(self):
        client = ExternalApiClient(imgbb_key="", giphy_key="k", github_token="t", bytebin_url="u", bytebin_username="", bytebin_password="")
        assert await client.upload_to_imgbb(b"x", "png") is None

    @pytest.mark.asyncio
    async def test_search_giphy_no_key(self):
        client = ExternalApiClient(imgbb_key="k", giphy_key="", github_token="t", bytebin_url="u", bytebin_username="", bytebin_password="")
        assert await client.search_giphy("cat") is None

    @pytest.mark.asyncio
    async def test_upload_bytebin_no_url(self, client: ExternalApiClient):
        client.bytebin_url = ""
        assert await client.upload_to_bytebin("data") is None

    @pytest.mark.asyncio
    async def test_upload_imgbb_bad_status(self, client: ExternalApiClient):
        mock_resp = _mock_resp(500)
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            assert await client.upload_to_imgbb(b"data", "png") is None

    @pytest.mark.asyncio
    async def test_search_giphy_invalid_json(self, client: ExternalApiClient):
        from pydantic import ValidationError

        mock_resp = _mock_resp(200, {"data": "bad"})
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_resp)
        with (
            patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session),
            patch("services.external_api_client.GiphyResponse.model_validate", side_effect=ValidationError.from_exception_data("GiphyResponse", [])),
        ):
            assert await client.search_giphy("cat") is None

    def test_create_github_issue_no_token(self):
        client = ExternalApiClient(imgbb_key="", giphy_key="", github_token="", bytebin_url="", bytebin_username="", bytebin_password="")
        client.create_github_issue("t", "b", [])

    @pytest.mark.asyncio
    async def test_upload_bytebin_invalid_response(self, client: ExternalApiClient):
        mock_resp = _mock_resp(201, {})
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_resp)
        with patch.object(client, "get_session", new_callable=AsyncMock, return_value=mock_session):
            assert await client.upload_to_bytebin("data") is None
