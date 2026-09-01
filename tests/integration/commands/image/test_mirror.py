"""Integration tests for commands.image.mirror."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.image.mirror import mirror as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image.mirror.ImageService.validate_attachment", return_value="typenotsupported"):
        await command_fn(info, image, "horizontal")
    embed_from_reply(info.reply)
