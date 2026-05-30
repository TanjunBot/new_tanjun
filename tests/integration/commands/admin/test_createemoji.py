import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp

from commands.admin.createemoji import create_emoji
from tests.helpers.discord import make_permissions, make_role
from tests.integration.commands.admin.conftest import make_aiohttp_session


pytestmark = pytest.mark.asyncio


async def test_create_emoji_missing_user_permission(restricted_command_info):
    await create_emoji(restricted_command_info, name="test", image_url="https://example.com/e.png")
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_success(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png")
    emoji_command_info.reply.assert_awaited_once()
    emoji_command_info.guild.create_custom_emoji.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_success_with_roles(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    role = make_role()
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png", roles=[role])
    emoji_command_info.guild.create_custom_emoji.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_bad_status(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session(status=404)
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png")
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_client_error(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session(side_effect=aiohttp.ClientError("fail"))
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png")
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_timeout(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session(side_effect=TimeoutError())
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png")
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.createemoji.aiohttp.ClientSession")
async def test_create_emoji_http_exception(mock_session_cls, emoji_command_info):
    import discord as discord_mod

    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.create_custom_emoji = AsyncMock(
        side_effect=discord_mod.HTTPException(MagicMock(), "error")
    )
    await create_emoji(emoji_command_info, name="test", image_url="https://example.com/e.png")
    emoji_command_info.reply.assert_awaited_once()
