from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_command_info, make_guild, make_member, make_text_channel

pytestmark = pytest.mark.asyncio


async def test_report_command_no_channel_configured():
    from commands.utility.report import report

    info = make_command_info()
    target = make_member()
    with (
        patch("commands.utility.report.check_if_reporter_is_blocked", new=AsyncMock(return_value=False)),
        patch("commands.utility.report.get_report_channel", new=AsyncMock(return_value=None)),
    ):
        await report(command_info=info, reason="test report", user=target)
    info.reply.assert_awaited()


async def test_report_command_blocked_reporter():
    from commands.utility.report import report

    info = make_command_info()
    target = make_member()
    with patch("commands.utility.report.check_if_reporter_is_blocked", new=AsyncMock(return_value=True)):
        await report(command_info=info, reason="test", user=target)
    info.reply.assert_awaited()
