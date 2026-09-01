from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.assertions import assert_reply_embed

pytestmark = pytest.mark.asyncio


@patch("commands.utility.brawlstars.unlink.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_unlink_not_linked(mock_linked, admin_command_info):
    from commands.utility.brawlstars.unlink import unlink

    mock_linked.return_value = None
    await unlink(admin_command_info)
    assert_reply_embed(admin_command_info)


@patch("commands.utility.brawlstars.unlink.remove_brawlstars_linked_account", new_callable=AsyncMock)
@patch("commands.utility.brawlstars.unlink.get_brawlstars_linked_account", new_callable=AsyncMock)
async def test_unlink_success(mock_linked, mock_remove, admin_command_info):
    from commands.utility.brawlstars.unlink import unlink

    mock_linked.return_value = "#ABC123"
    await unlink(admin_command_info)
    assert_reply_embed(admin_command_info)
    mock_remove.assert_awaited_once()
