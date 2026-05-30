from __future__ import annotations

from typing import Any
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_aiohttp_session():
    with patch("aiohttp.ClientSession") as mock_session:
        yield mock_session


def openai_response(content: str = "Hello from AI") -> dict[str, Any]:
    return {
        "choices": [{"message": {"content": content}}],
        "usage": {"total_tokens": 10},
    }


def twitch_stream_response(is_live: bool = True) -> dict[str, Any]:
    if is_live:
        return {"data": [{"id": "123", "user_name": "test", "title": "Live"}]}
    return {"data": []}


def brawlstars_player_response() -> dict[str, Any]:
    return {
        "tag": "#TEST",
        "name": "Player",
        "trophies": 5000,
        "highestTrophies": 6000,
    }


def giphy_response() -> dict[str, Any]:
    return {"data": [{"images": {"original": {"url": "https://example.com/gif.gif"}}}]}


def github_user_response() -> dict[str, Any]:
    return {"login": "testuser", "id": 1}
