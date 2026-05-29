"""Typed external API client for ImgBB, Giphy, Bytebin, and GitHub."""

from __future__ import annotations

import gzip

from typing import Any

import aiohttp
from aiohttp import ClientTimeout
from github import Github
from pydantic import BaseModel


class ImgBBResponse(BaseModel):
    """Response model for ImgBB upload API."""

    id: str | None = None
    url: str | None = None
    display_url: str | None = None
    delete_url: str | None = None


class GiphyGifImage(BaseModel):
    """Single image variant from Giphy."""

    url: str
    width: str | None = None
    height: str | None = None


class GifData(BaseModel):
    """Single GIF entry in a Giphy response."""

    id: str
    url: str
    title: str | None = None
    images: dict[str, Any]


class GiphyResponse(BaseModel):
    """Response model for Giphy search API."""

    data: list[GifData] = []
    pagination: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


class BytebinRequest(BaseModel):
    """Request body model for Bytebin."""

    content: str
    content_type: str = "text/html"
    content_encoding: str | None = None


class BytebinResponse(BaseModel):
    """Response model for Bytebin API."""

    key: str


class ExternalApiClient:
    """Centralized HTTP client for external API calls.

    Provides typed responses for ImgBB, Giphy, Bytebin, and GitHub APIs
    with a shared aiohttp session for connection pooling.
    """

    def __init__(
        self,
        imgbb_key: str = "",
        giphy_key: str = "",
        github_token: str = "",
        bytebin_url: str = "",
        bytebin_username: str = "",
        bytebin_password: str = "",
    ) -> None:
        self.imgbb_key = imgbb_key
        self.giphy_key = giphy_key
        self.github_token = github_token
        self.bytebin_url = bytebin_url
        self.bytebin_username = bytebin_username
        self.bytebin_password = bytebin_password
        self._session: aiohttp.ClientSession | None = None

    async def get_session(self) -> aiohttp.ClientSession:
        """Return an existing or new aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=ClientTimeout(total=30))
        return self._session

    async def upload_to_imgbb(self, image: bytes, file_extension: str = "png") -> ImgBBResponse | None:
        """Upload an image to ImgBB and return a typed response.

        Args:
            image: Raw image bytes.
            file_extension: File extension for the upload filename.

        Returns:
            ImgBBResponse on success, None on failure.
        """
        if not self.imgbb_key:
            return None
        try:
            session = await self.get_session()
            form_data = aiohttp.FormData()
            form_data.add_field("key", self.imgbb_key)
            form_data.add_field("image", image, filename=f"upload.{file_extension}")
            form_data.add_field("name", "tbg")

            async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
                if response.status != 200:
                    return None
                raw = await response.json()
        except (TimeoutError, aiohttp.ClientError):
            return None

        data = raw.get("data", {}) if isinstance(raw, dict) else {}
        return ImgBBResponse(
            id=data.get("id"),
            url=data.get("url"),
            display_url=data.get("display_url"),
            delete_url=data.get("delete_url"),
        )

    async def search_giphy(self, query: str, limit: int = 10, rating: str = "pg") -> GiphyResponse | None:
        """Search Giphy for GIFs and return a typed response.

        Args:
            query: Search query string.
            limit: Maximum number of results.
            rating: Content rating filter.

        Returns:
            GiphyResponse on success, None on failure.
        """
        if not self.giphy_key:
            return None
        try:
            session = await self.get_session()
            params = {"api_key": self.giphy_key, "q": query, "limit": str(limit), "rating": rating}
            async with session.get("https://api.giphy.com/v1/gifs/search", params=params) as response:
                if response.status != 200:
                    return None
                raw = await response.json()
        except (TimeoutError, aiohttp.ClientError):
            return None

        if not isinstance(raw, dict):
            return None
        return GiphyResponse.model_validate(raw)

    async def upload_to_bytebin(self, data: str) -> str | None:
        """Upload compressed content to Bytebin and return the URL.

        Args:
            data: String content to compress and upload.

        Returns:
            Full URL key string on success, None on failure.
        """
        if not self.bytebin_url:
            return None
        compressed_content = gzip.compress(data.encode("utf-8"))
        try:
            session = await self.get_session()
            auth = aiohttp.BasicAuth(self.bytebin_username, self.bytebin_password)
            headers = {"Content-Type": "text/html", "Content-Encoding": "gzip"}

            async with session.post(
                self.bytebin_url + "/post",
                data=compressed_content,
                headers=headers,
                auth=auth,
            ) as response:
                if response.status != 201:
                    return None
                raw = await response.json()
        except (TimeoutError, aiohttp.ClientError):
            return None

        if not isinstance(raw, dict) or "key" not in raw:
            return None
        return f"{self.bytebin_url}/{raw['key']}"

    def create_github_issue(self, title: str, body: str, labels: list[str]) -> None:
        """Create a GitHub issue (synchronous; run in executor).

        Args:
            title: Issue title.
            body: Issue body markdown.
            labels: List of label names to attach.
        """
        if not self.github_token:
            return
        g = Github(self.github_token)
        repo = g.get_repo("TanjunBot/new_tanjun")
        label_objects = [repo.get_label(label) for label in labels]
        repo.create_issue(title=title, body=body, labels=label_objects)

    async def close(self) -> None:
        """Close the aiohttp session if open."""
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
