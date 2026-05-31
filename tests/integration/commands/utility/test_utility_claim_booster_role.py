"""Integration tests for commands.utility.claim_booster_role.claimBoosterRole."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from tests.helpers.assertions import assert_reply_embed


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_claimBoosterRole_no_booster_configured(restricted_command_info):
    info = restricted_command_info
    with patch("commands.utility.claim_booster_role.booster_service") as svc:
        svc.get = AsyncMock(return_value=None)
        from commands.utility.claim_booster_role import claimBoosterRole as command_fn

        await command_fn(info, name="Test", color=None, icon=None)
    assert_reply_embed(info)
    svc.get.assert_awaited_once()


async def test_claimBoosterRole_not_a_booster(admin_command_info):
    info = admin_command_info
    info.user.premium_since = None
    with patch("commands.utility.claim_booster_role.booster_service") as svc:
        svc.get = AsyncMock(return_value="999")
        svc.get_claim_for_user = AsyncMock(return_value=None)
        from commands.utility.claim_booster_role import claimBoosterRole as command_fn

        await command_fn(info, name="Test", color="FF0000", icon=None)
    assert_reply_embed(info)


async def test_claimBoosterRole_no_guild_raises(no_guild_command_info):
    with patch("commands.utility.claim_booster_role.booster_service") as svc:
        svc.get = AsyncMock(return_value="999")
        from commands.utility.claim_booster_role import claimBoosterRole as command_fn

        with pytest.raises(AttributeError):
            await command_fn(no_guild_command_info, name="Test", color=None, icon=None)
