"""Integration tests for commands.image.compress."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.image.compress import compress as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image.compress.ImageService.validate_attachment", return_value="invalid"):
        await command_fn(info, image, 80)
    embed_from_reply(info.reply)
