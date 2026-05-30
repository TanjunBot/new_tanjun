from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from commands.level.level_set_xp_cooldown import set_text_cooldown_command, set_voice_cooldown_command
from tests.helpers.discord import make_permissions


pytestmark = pytest.mark.asyncio


def _deny_admin(info):
    perms = make_permissions(administrator=False)
    info.channel.permissions_for = MagicMock(return_value=perms)


@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_text_cooldown_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await set_text_cooldown_command(admin_command_info, 60)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_text_cooldown_invalid(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    await set_text_cooldown_command(admin_command_info, -1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_text_cooldown", new_callable=AsyncMock)
@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_text_cooldown_success(mock_isinstance, mock_set, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    await set_text_cooldown_command(admin_command_info, 30)
    mock_set.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_voice_cooldown_no_permission(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    _deny_admin(admin_command_info)
    await set_voice_cooldown_command(admin_command_info, 60)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_voice_cooldown_invalid(mock_isinstance, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    await set_voice_cooldown_command(admin_command_info, -5)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_voice_cooldown", new_callable=AsyncMock)
@patch("commands.level.level_set_xp_cooldown.isinstance")
async def test_voice_cooldown_success(mock_isinstance, mock_set, admin_command_info):
    mock_isinstance.side_effect = lambda obj, cls: cls is discord.Member or cls is discord.abc.GuildChannel
    await set_voice_cooldown_command(admin_command_info, 45)
    mock_set.assert_awaited_once()
