from __future__ import annotations

import time
from collections import deque
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.channel import dynamicslowmode as ds_mod
from commands.channel.dynamicslowmode import (
    addDynamicslowmode,
    dynamicslowmodeMessage,
    getDynamicslowmode_channels,
    removeDynamicslowmode,
)
from tests.helpers.discord import make_permissions, make_text_channel


pytestmark = pytest.mark.asyncio


async def test_add_success(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=None):
        with patch.object(ds_mod._ds_service, "configure", new_callable=AsyncMock) as mock_cfg:
            await addDynamicslowmode(admin_command_info, channel, 5, 10, 60)
            mock_cfg.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_add_already_set(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=MagicMock()):
        await addDynamicslowmode(admin_command_info, channel, 5, 10)
    admin_command_info.reply.assert_awaited_once()


async def test_add_bot_missing_permissions(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    channel.permissions_for = MagicMock(return_value=make_permissions(manage_messages=False))
    await addDynamicslowmode(admin_command_info, channel, 5, 10)
    admin_command_info.reply.assert_awaited_once()


async def test_remove_success(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=MagicMock()):
        with patch.object(ds_mod._ds_service, "remove", new_callable=AsyncMock) as mock_rm:
            await removeDynamicslowmode(admin_command_info, channel)
            mock_rm.assert_awaited_once()


async def test_remove_not_set(admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=None):
        await removeDynamicslowmode(admin_command_info, channel)
    admin_command_info.reply.assert_awaited_once()


async def test_get_channels_empty(admin_command_info):
    with patch.object(ds_mod._ds_service, "get_all_configs", new_callable=AsyncMock, return_value=[]):
        await getDynamicslowmode_channels(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_get_channels_list(admin_command_info):
    cfg = MagicMock(channel_id="123", messages=5, per=10, reset_after=60)
    with patch.object(ds_mod._ds_service, "get_all_configs", new_callable=AsyncMock, return_value=[cfg]):
        await getDynamicslowmode_channels(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_dynamicslowmode_message_no_config():
    message = MagicMock()
    message.channel.id = 1
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=None):
        await dynamicslowmodeMessage(message)


async def test_dynamicslowmode_message_throttle():
    message = MagicMock()
    message.channel.id = 99
    message.channel.slowmode_delay = 0
    message.channel.edit = AsyncMock()
    message.guild.preferred_locale = "en-US"
    config = MagicMock(messages=2, per=5, reset_after=60, cached_slowmode=0)
    ds_mod._ds_service._recent_messages = {99: deque([time.time(), time.time(), time.time()])}
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=config):
        with patch.object(ds_mod._ds_service, "cache_current_slowmode", new_callable=AsyncMock):
            await dynamicslowmodeMessage(message)
    message.channel.edit.assert_awaited()


async def test_dynamicslowmode_message_reset():
    message = MagicMock()
    message.channel.id = 100
    message.channel.slowmode_delay = 5
    message.channel.edit = AsyncMock()
    message.guild.preferred_locale = "en-US"
    config = MagicMock(messages=10, per=5, reset_after=60, cached_slowmode=0)
    ds_mod._ds_service._recent_messages = {100: deque([time.time()])}
    with patch.object(ds_mod._ds_service, "get_config", new_callable=AsyncMock, return_value=config):
        with patch.object(ds_mod._ds_service, "restore_slowmode", new_callable=AsyncMock) as mock_restore:
            await dynamicslowmodeMessage(message)
    message.channel.edit.assert_awaited()
    mock_restore.assert_awaited_once()
