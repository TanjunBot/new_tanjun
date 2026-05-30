from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.helpers.discord import make_interaction, make_permissions


def make_aiohttp_session(status: int = 200, data: bytes = b"fake", side_effect: Exception | None = None):
    mock_resp = AsyncMock()
    mock_resp.status = status
    mock_resp.read = AsyncMock(return_value=data)
    mock_session = MagicMock()
    if side_effect:
        mock_session.get.side_effect = side_effect
    else:
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session.get.return_value.__aexit__ = AsyncMock(return_value=None)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    return mock_session


def make_report(
    report_id: int = 1,
    user_id: int = 222222222,
    reporter_id: int = 333333333,
    reason: str = "spam",
    accepted: bool = False,
    resolved: bool = False,
) -> MagicMock:
    report = MagicMock()
    report.id = report_id
    report.guild_id = 123456789
    report.user_id = user_id
    report.reporter_id = reporter_id
    report.reason = reason
    report.created_at = 1700000000
    report.accepted = accepted
    report.accepted_at = 1700000100 if accepted else None
    report.resolved = resolved
    report.resolved_at = 1700000200 if resolved else None
    return report


def make_detailed_warning(
    warning_id: int = 1,
    reason: str = "test reason",
    expired: bool = False,
) -> MagicMock:
    warning = MagicMock()
    warning.id = warning_id
    warning.reason = reason
    warning.created_by = 111111111
    warning.created_at = datetime(2024, 1, 1)
    if expired:
        warning.expires_at = datetime(2020, 1, 1)
    else:
        warning.expires_at = datetime(2030, 1, 1)
    return warning


def make_trigger_message(
    trigger_id: int = 1,
    trigger: str = "hello",
    response: str = "world",
    case_sensitive: bool = False,
) -> MagicMock:
    tm = MagicMock()
    tm.id = trigger_id
    tm.trigger = trigger
    tm.response = response
    tm.case_sensitive = case_sensitive
    return tm


def make_trigger_channel(channel_id: int = 444444444) -> MagicMock:
    tc = MagicMock()
    tc.channel_id = channel_id
    return tc


async def empty_async_iter():
    if False:
        yield


async def async_iter_from(items: list[Any]):
    for item in items:
        yield item


def make_view_interaction(user: MagicMock | None = None, guild: MagicMock | None = None) -> MagicMock:
    interaction = make_interaction(user=user, guild=guild)
    interaction.response.send_message = AsyncMock()
    interaction.response.edit_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    interaction.response.edit_original_response = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send_message = AsyncMock()
    interaction.followup.send = AsyncMock()
    return interaction


@pytest.fixture
def manage_emojis_permissions(full_permissions: MagicMock) -> MagicMock:
    perms = make_permissions(
        administrator=full_permissions.administrator,
        manage_emojis=True,
        manage_roles=getattr(full_permissions, "manage_roles", True),
        manage_messages=getattr(full_permissions, "manage_messages", True),
        manage_guild=getattr(full_permissions, "manage_guild", True),
        manage_channels=getattr(full_permissions, "manage_channels", True),
        kick_members=getattr(full_permissions, "kick_members", True),
        moderate_members=getattr(full_permissions, "moderate_members", True),
    )
    return perms


@pytest.fixture
def emoji_command_info(admin_command_info, manage_emojis_permissions: MagicMock) -> MagicMock:
    admin_command_info.channel.permissions_for = MagicMock(return_value=manage_emojis_permissions)
    admin_command_info.guild.me.guild_permissions = manage_emojis_permissions
    admin_command_info.guild.emojis = []
    admin_command_info.guild.emoji_limit = 50
    admin_command_info.guild.create_custom_emoji = AsyncMock(return_value=MagicMock(__str__=lambda s: "<:new:999>"))
    return admin_command_info
