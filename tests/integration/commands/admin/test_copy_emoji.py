import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from commands.admin.copy_emoji import copy_emoji
from tests.helpers.discord import make_permissions
from tests.integration.commands.admin.conftest import make_aiohttp_session


pytestmark = pytest.mark.asyncio

_SAMPLE_EMOJI = "<:testemoji:123456789012345678>"
_ANIMATED_EMOJI = "<a:animated:987654321098765432>"


async def test_copy_emoji_missing_user_permission(restricted_command_info):
    await copy_emoji(restricted_command_info, emoji=_SAMPLE_EMOJI)
    restricted_command_info.reply.assert_awaited_once()


async def test_copy_emoji_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_emojis=False)
    await copy_emoji(admin_command_info, emoji=_SAMPLE_EMOJI)
    admin_command_info.reply.assert_awaited_once()


async def test_copy_emoji_no_emojis_in_string(admin_command_info):
    await copy_emoji(admin_command_info, emoji="not an emoji")
    admin_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_success_single(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    await copy_emoji(emoji_command_info, emoji=_SAMPLE_EMOJI)
    emoji_command_info.reply.assert_awaited_once()
    emoji_command_info.guild.create_custom_emoji.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_success_multiple(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.create_custom_emoji = AsyncMock(
        side_effect=[MagicMock(__str__=lambda s: "<:a:1>"), MagicMock(__str__=lambda s: "<:b:2>")]
    )
    await copy_emoji(emoji_command_info, emoji=f"{_SAMPLE_EMOJI} {_SAMPLE_EMOJI}")
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_partial_success(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session(status=404)
    emoji_command_info.guild.create_custom_emoji = AsyncMock(return_value=MagicMock(__str__=lambda s: "<:a:1>"))
    await copy_emoji(emoji_command_info, emoji=f"{_SAMPLE_EMOJI} {_SAMPLE_EMOJI}")
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_limit_reached(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.emojis = [MagicMock(animated=False)] * 50
    emoji_command_info.guild.emoji_limit = 1
    await copy_emoji(emoji_command_info, emoji=_SAMPLE_EMOJI)
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_animated_limit(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.emojis = [MagicMock(animated=True)] * 50
    emoji_command_info.guild.emoji_limit = 1
    await copy_emoji(emoji_command_info, emoji=_ANIMATED_EMOJI)
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_create_exception(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.create_custom_emoji = AsyncMock(side_effect=RuntimeError("fail"))
    await copy_emoji(emoji_command_info, emoji=_SAMPLE_EMOJI)
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_unexpected_error(mock_session_cls, emoji_command_info):
    mock_session_cls.side_effect = RuntimeError("session fail")
    await copy_emoji(emoji_command_info, emoji=_SAMPLE_EMOJI)
    emoji_command_info.reply.assert_awaited_once()


@patch("commands.admin.copy_emoji.aiohttp.ClientSession")
async def test_copy_emoji_animated_success(mock_session_cls, emoji_command_info):
    mock_session_cls.return_value = make_aiohttp_session()
    emoji_command_info.guild.create_custom_emoji = AsyncMock(return_value=MagicMock(__str__=lambda s: "<a:a:1>"))
    await copy_emoji(emoji_command_info, emoji=_ANIMATED_EMOJI)
    emoji_command_info.guild.create_custom_emoji.assert_awaited_once()
