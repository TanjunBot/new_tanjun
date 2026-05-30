"""Integration tests for commands.image.mirror."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.image.mirror import mirror as command_fn


@pytest.mark.asyncio
async def test_validation_error():
    image = MagicMock()
    info = make_command_info()
    with patch("commands.image.mirror.ImageService.validate_attachment", return_value="invalid"):
        await command_fn(info, image, "horizontal")
    embed_from_reply(info.reply)
