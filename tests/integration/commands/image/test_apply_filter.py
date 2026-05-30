"""Integration tests for commands.image._filter."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.image._filter import apply_filter as command_fn
from tests.integration.commands.conftest import embed_from_reply
from tests.helpers.discord import make_command_info


@pytest.mark.asyncio
async def test_apply_filter_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image._filter.ImageService.validate_attachment", return_value="invalid"):
        await command_fn(info, image, "blur")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_apply_filter_success():
    image = MagicMock()
    image.read = AsyncMock(return_value=b"pngbytes")
    info = make_command_info()
    with (
        patch("commands.image._filter.ImageService.validate_attachment", return_value=None),
        patch("commands.image._filter.ImageService.process", new_callable=AsyncMock, return_value=b"out"),
    ):
        await command_fn(info, image, "blur")
    embed_from_reply(info.reply)
