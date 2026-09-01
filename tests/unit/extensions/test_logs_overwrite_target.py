"""Regression tests for extensions.logs._overwrite_target_str.

See issue #3266: permission-overwrite targets can be a bare ``discord.Object``
(neither ``.name`` nor ``.mention``) when the referenced role/member is
uncached or deleted, which previously raised ``AttributeError``.
"""
from __future__ import annotations

from types import SimpleNamespace

import discord
import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from extensions.logs import _overwrite_target_str  # noqa: E402

pytestmark = pytest.mark.unit


def test_object_without_name_or_mention_falls_back_to_id() -> None:
    # A bare overwrite target (e.g. an uncached discord.Object) exposes an
    # id but neither .name nor .mention.
    target = SimpleNamespace(id=123456789)
    assert _overwrite_target_str(target) == 'ID: 123456789'


def test_target_with_mention_uses_mention() -> None:
    target = SimpleNamespace(mention='<@&5>')
    assert _overwrite_target_str(target) == '<@&5>'


def test_target_with_name_but_no_mention_uses_name() -> None:
    target = SimpleNamespace(name='somebody')
    assert _overwrite_target_str(target) == 'somebody'


def test_target_prefers_mention_over_name() -> None:
    target = SimpleNamespace(mention='<@42>', name='ignored')
    assert _overwrite_target_str(target) == '<@42>'


def test_target_without_name_or_mention_or_id_is_unknown() -> None:
    target = SimpleNamespace()
    assert _overwrite_target_str(target) == 'ID: ?'


@pytest.mark.asyncio
async def test_find_audit_log_entry_handles_discord_server_error() -> None:
    from unittest.mock import MagicMock
    from extensions.logs import _find_audit_log_entry

    guild = MagicMock()

    async def fake_audit_logs(*args, **kwargs):
        resp = MagicMock()
        resp.status = 503
        raise discord.DiscordServerError(resp, "503 Service Unavailable")
        yield  # make it an async generator

    guild.audit_logs = fake_audit_logs
    result = await _find_audit_log_entry(guild, discord.AuditLogAction.channel_update, lambda e: True)
    assert result is None


@pytest.mark.asyncio
async def test_find_audit_log_entry_handles_forbidden() -> None:
    from unittest.mock import MagicMock
    from extensions.logs import _find_audit_log_entry

    guild = MagicMock()

    async def fake_audit_logs(*args, **kwargs):
        resp = MagicMock()
        resp.status = 403
        raise discord.Forbidden(resp, "Missing Permissions")
        yield

    guild.audit_logs = fake_audit_logs
    result = await _find_audit_log_entry(guild, discord.AuditLogAction.channel_update, lambda e: True)
    assert result is None