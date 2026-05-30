"""Integration tests for commands.image.background."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.image.background import background as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image.background.ImageService.validate_attachment", return_value="invalid"):
        await command_fn(info, image)
    embed_from_reply(info.reply)
