"""Integration tests for commands.image.resize."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.image.resize import resize as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_invalid_attachment():
    image = MagicMock()
    image.read = AsyncMock(return_value=b"")
    info = make_command_info()
    with patch("commands.image.resize.ImageService.validate_attachment", return_value="filesize"):
        await command_fn(info, image, 100, 100)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_success():
    image = MagicMock()
    image.read = AsyncMock(return_value=b"fakepng")
    info = make_command_info()
    with (
        patch("commands.image.resize.ImageService.validate_attachment", return_value=None),
        patch("commands.image.resize.ImageService.process", new_callable=AsyncMock, return_value=b"out"),
    ):
        await command_fn(info, image, 10, 10)
    embed_from_reply(info.reply)
