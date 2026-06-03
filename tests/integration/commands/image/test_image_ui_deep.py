from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.image.resize import resize
from tests.helpers.view_state import embed_from_reply

pytestmark = pytest.mark.asyncio


async def test_resize_invalid_attachment_embed() -> None:
    from tests.helpers.discord import make_command_info

    image = MagicMock()
    image.read = AsyncMock(return_value=b"")
    info = make_command_info()
    with patch("commands.image.resize.ImageService.validate_attachment", return_value="filesize"):
        await resize(info, image, 100, 100)
    embed_from_reply(info)


async def test_resize_success_calls_reply() -> None:
    from tests.helpers.discord import make_command_info

    image = MagicMock()
    image.read = AsyncMock(return_value=b"fakepng")
    info = make_command_info()
    with (
        patch("commands.image.resize.ImageService.validate_attachment", return_value=None),
        patch("commands.image.resize.ImageService.process", new_callable=AsyncMock, return_value=b"out"),
    ):
        await resize(info, image, 10, 10)
    info.reply.assert_awaited_once()
