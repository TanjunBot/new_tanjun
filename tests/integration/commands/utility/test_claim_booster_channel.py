from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_command_info, make_guild, make_member

pytestmark = pytest.mark.asyncio


async def test_claim_booster_channel_not_configured():
    from commands.utility.claim_booster_channel import claimBoosterChannel

    info = make_command_info()
    with patch("commands.utility.claim_booster_channel.booster_service") as svc:
        svc.get = AsyncMock(return_value=None)
        await claimBoosterChannel(command_info=info, name="my-channel")
    info.reply.assert_awaited()


async def test_claim_booster_channel_success():
    from commands.utility.claim_booster_channel import claimBoosterChannel

    guild = make_guild()
    member = make_member()
    member.premium_since = MagicMock()
    info = make_command_info(guild=guild, user=member)
    booster = MagicMock()
    with patch("commands.utility.claim_booster_channel.booster_service") as svc:
        svc.get = AsyncMock(return_value=booster)
        svc.get_claim_for_user = AsyncMock(return_value=None)
        svc.claim = AsyncMock(return_value=True)
        await claimBoosterChannel(command_info=info, name="my-channel")
    info.reply.assert_awaited()
