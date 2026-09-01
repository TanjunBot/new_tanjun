from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.admin.copy_7tv_emote import copy_7tv_emote
from services.seventv_service import SevenTVEmote, SevenTVUser
from tests.helpers.assertions import assert_reply_embed
from tests.helpers.discord import make_permissions

pytestmark = pytest.mark.asyncio


def _seventv_user(emote_count: int = 2) -> SevenTVUser:
    emotes = [
        SevenTVEmote(id=f"e{i}", name=f"emote{i}", animated=False, owner_name="Owner", image_url=f"https://cdn.test/{i}.png")
        for i in range(emote_count)
    ]
    return SevenTVUser(
        id="u1",
        username="streamer",
        display_name="Streamer",
        avatar_url="https://cdn.test/avatar.png",
        emote_set_id="set1",
        emotes=emotes,
    )


async def test_missing_user_permission(restricted_command_info):
    await copy_7tv_emote(restricted_command_info, "streamer")
    assert_reply_embed(restricted_command_info)


async def test_missing_bot_permission(admin_command_info):
    admin_command_info.channel.permissions_for = MagicMock(
        return_value=make_permissions(administrator=True, manage_emojis=True)
    )
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_emojis=False)
    await copy_7tv_emote(admin_command_info, "streamer")
    assert_reply_embed(admin_command_info)


@patch("commands.admin.copy_7tv_emote.get_seventv_service")
async def test_user_not_found(mock_get_service, emoji_command_info):
    mock_service = MagicMock()
    mock_service.get_user_by_twitch = AsyncMock(return_value=None)
    mock_get_service.return_value = mock_service
    await copy_7tv_emote(emoji_command_info, "unknown")
    assert_reply_embed(emoji_command_info)


@patch("commands.admin.copy_7tv_emote.get_seventv_service")
async def test_success(mock_get_service, emoji_command_info):
    mock_service = MagicMock()
    mock_service.get_user_by_twitch = AsyncMock(return_value=_seventv_user())
    mock_get_service.return_value = mock_service
    await copy_7tv_emote(emoji_command_info, "streamer")
    emoji_command_info.reply.assert_awaited_once()
    assert emoji_command_info.reply.await_args.kwargs.get("embed") is not None
    assert emoji_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.admin.copy_7tv_emote.get_seventv_service")
async def test_empty_emotes(mock_get_service, emoji_command_info):
    user = _seventv_user(emote_count=0)
    mock_service = MagicMock()
    mock_service.get_user_by_twitch = AsyncMock(return_value=user)
    mock_get_service.return_value = mock_service
    await copy_7tv_emote(emoji_command_info, "streamer")
    assert_reply_embed(emoji_command_info)
