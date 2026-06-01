from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.minigames import _counting_common as cmd_common
from minigames import _counting_common as pkg_common
from minigames._counting_common import _handle_guild_check, _handle_opted_out
from tests.helpers.discord import make_guild, make_message

pytestmark = pytest.mark.asyncio


async def test_cmd_require_moderate_members_denied():
    from tests.helpers.discord import make_command_info, make_member, make_permissions, make_text_channel

    perms = make_permissions(moderate_members=False)
    user = make_member()
    user.guild_permissions = perms
    guild = make_text_channel().guild
    channel = make_text_channel(guild=guild)
    channel.permissions_for = MagicMock(return_value=perms)
    info = make_command_info(user=user, guild=guild, channel=channel, reply=AsyncMock())
    assert await cmd_common.require_moderate_members(info, "minigames.setcountingchannel") is True


async def test_pkg_handle_guild_check_dm():
    message = make_message()
    message.guild = None
    with patch("minigames._counting_common.DiscordSafe.send", new_callable=AsyncMock) as send:
        assert await _handle_guild_check(message) is True
        send.assert_awaited_once()


async def test_pkg_handle_opted_out():
    message = make_message(guild=make_guild())
    with (
        patch("minigames._counting_common.check_if_opted_out", new_callable=AsyncMock, return_value=True),
        patch("minigames._counting_common.DiscordSafe.send_dm", new_callable=AsyncMock),
        patch("minigames._counting_common.DiscordSafe.delete", new_callable=AsyncMock),
    ):
        assert await _handle_opted_out(message, "en_US") is True


async def test_pkg_counting_wrong_number():
    message = make_message(content="99", author=MagicMock(id=1))
    message.guild = make_guild()
    message.guild.preferred_locale = "en_US"
    with (
        patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
        patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
        patch("minigames._counting_common.DiscordSafe.delete", new_callable=AsyncMock) as delete,
    ):
        await pkg_common.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value="1"),
            increase_progress_func=AsyncMock(),
        )
        delete.assert_awaited()


async def test_pkg_counting_double_count():
    author = MagicMock(id=42)
    message = make_message(content="1", author=author)
    message.guild = make_guild()
    with (
        patch("minigames._counting_common._handle_guild_check", new_callable=AsyncMock, return_value=False),
        patch("minigames._counting_common._handle_opted_out", new_callable=AsyncMock, return_value=False),
        patch("minigames._counting_common.DiscordSafe.delete", new_callable=AsyncMock) as delete,
    ):
        await pkg_common.counting(
            message,
            get_progress_func=AsyncMock(return_value=0),
            get_last_counter_id_func=AsyncMock(return_value="42"),
            increase_progress_func=AsyncMock(),
        )
        delete.assert_awaited()
