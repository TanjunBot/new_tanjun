"""Integration tests for commands.image.rescale."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from commands.image.rescale import rescale as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image.rescale.ImageService.validate_attachment", return_value="invalid"):
        await command_fn(info, image, 0.5)
    embed_from_reply(info.reply)
