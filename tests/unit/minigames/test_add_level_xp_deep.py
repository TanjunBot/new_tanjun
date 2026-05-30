from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from minigames import add_level_xp
from tests.helpers.discord import make_member, make_text_channel


pytestmark = pytest.mark.asyncio


def _message(guild=None, author=None, channel=None) -> MagicMock:
    msg = MagicMock()
    msg.guild = guild
    msg.author = author or make_member()
    msg.channel = channel or make_text_channel()
    return msg


@pytest.fixture(autouse=True)
def _clear_notified():
    add_level_xp.clearNotifiedUsers()
    yield
    add_level_xp.clearNotifiedUsers()


@patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=True)
async def test_add_level_xp_opted_out(mock_opt):
    await add_level_xp.addLevelXp(_message())
    mock_opt.assert_awaited_once()


async def test_add_level_xp_no_guild():
    msg = _message(guild=None)
    await add_level_xp.addLevelXp(msg)


@patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock, return_value=False)
@patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False)
async def test_add_level_xp_system_disabled(mock_opt, mock_status):
    guild = MagicMock()
    guild.id = 1
    await add_level_xp.addLevelXp(_message(guild=guild))


@patch("minigames.add_level_xp.is_entity_blacklisted", new_callable=AsyncMock, return_value=True)
@patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock, return_value=True)
@patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False)
async def test_add_level_xp_blacklisted(mock_opt, mock_status, mock_bl):
    guild = MagicMock()
    guild.id = 1
    await add_level_xp.addLevelXp(_message(guild=guild))


@patch("minigames.add_level_xp.handle_level_up", new_callable=AsyncMock)
@patch("minigames.add_level_xp.get_level_for_xp_async", new_callable=AsyncMock, side_effect=[1, 1])
@patch("minigames.add_level_xp.update_user_xp", new_callable=AsyncMock)
@patch("minigames.add_level_xp.get_user_xp", new_callable=AsyncMock, return_value=10)
@patch("minigames.add_level_xp.fetch_xp_details", new_callable=AsyncMock, return_value=("medium", None, 5))
@patch("minigames.add_level_xp.is_entity_blacklisted", new_callable=AsyncMock, return_value=False)
@patch("minigames.add_level_xp.get_level_system_status", new_callable=AsyncMock, return_value=True)
@patch("minigames.add_level_xp.check_if_opted_out", new_callable=AsyncMock, return_value=False)
async def test_add_level_xp_no_level_up(
    mock_opt,
    mock_status,
    mock_bl,
    mock_fetch,
    mock_get_xp,
    mock_update,
    mock_level,
    mock_handle,
):
    guild = MagicMock()
    guild.id = 1
    await add_level_xp.addLevelXp(_message(guild=guild))
    mock_update.assert_awaited_once()
    mock_handle.assert_not_awaited()


@patch("minigames.add_level_xp.update_user_roles", new_callable=AsyncMock)
@patch("minigames.add_level_xp.format_level_up_message", new_callable=AsyncMock, return_value="Level up!")
@patch("minigames.add_level_xp.determine_levelup_channel", new_callable=AsyncMock)
@patch("minigames.add_level_xp.get_levelup_message_status", new_callable=AsyncMock, return_value=True)
async def test_handle_level_up(mock_status, mock_channel, mock_format, mock_roles):
    channel = MagicMock()
    channel.send = AsyncMock()
    mock_channel.return_value = channel
    guild = MagicMock()
    guild.id = 1
    guild.preferred_locale = "en_US"
    author = make_member(user_id=42)
    msg = _message(guild=guild, author=author)
    await add_level_xp.handle_level_up(msg, 5)
    channel.send.assert_awaited_once()
    mock_roles.assert_awaited_once()


@patch("minigames.add_level_xp.get_levelup_channel", new_callable=AsyncMock, return_value=None)
async def test_determine_levelup_channel_default(mock_cfg):
    guild = MagicMock()
    guild.get_channel = MagicMock(return_value=None)
    msg = _message(guild=guild)
    ch = await add_level_xp.determine_levelup_channel(msg, "1")
    assert ch is msg.channel


@patch("minigames.add_level_xp.get_levelup_channel", new_callable=AsyncMock, return_value="999")
async def test_determine_levelup_channel_configured(mock_cfg):
    class Messageable:
        pass

    configured = Messageable()
    with patch("minigames.add_level_xp.discord.abc.Messageable", Messageable):
        guild = MagicMock()
        guild.get_channel = MagicMock(return_value=configured)
        msg = _message(guild=guild)
        ch = await add_level_xp.determine_levelup_channel(msg, "1")
    assert ch is configured


@patch("minigames.add_level_xp.get_levelup_message", new_callable=AsyncMock, return_value="Hi {user} lvl {level}")
async def test_format_level_up_message_custom(mock_msg):
    guild = MagicMock()
    guild.preferred_locale = "en_US"
    text = await add_level_xp.format_level_up_message("1", "<@1>", 3, guild)
    assert "lvl 3" in text


@patch("minigames.add_level_xp.get_levelup_message", new_callable=AsyncMock, return_value=None)
async def test_format_level_up_message_default(mock_msg):
    guild = MagicMock()
    guild.preferred_locale = "en_US"
    text = await add_level_xp.format_level_up_message("1", "<@1>", 3, guild)
    assert isinstance(text, str)


async def test_update_user_roles_add_and_remove():
    role_low = MagicMock()
    role_low.id = 10
    role_high = MagicMock()
    role_high.id = 20
    guild = MagicMock()
    guild.id = 1
    guild.preferred_locale = "en_US"
    guild.get_role = MagicMock(side_effect=lambda rid: role_low if rid == 10 else role_high)
    author = make_member(user_id=1)
    author.roles = []
    author.add_roles = AsyncMock()
    author.remove_roles = AsyncMock()
    msg = _message(guild=guild, author=author)

    async def role_iter():
        lr1 = MagicMock(level=2, role_id="10")
        lr2 = MagicMock(level=10, role_id="20")
        yield lr1
        yield lr2

    with patch("minigames.add_level_xp.get_level_roles", return_value=role_iter()):
        await add_level_xp.update_user_roles(msg, 5, "1")
    author.add_roles.assert_awaited()


@patch("minigames.add_level_xp.calculate_xp", new_callable=AsyncMock, return_value=7)
@patch("minigames.add_level_xp._get_cached_config", new_callable=AsyncMock, side_effect=["medium", None])
async def test_fetch_xp_details(mock_cfg, mock_calc):
    guild = MagicMock()
    guild.id = 1
    scaling, formula, xp = await add_level_xp.fetch_xp_details(_message(guild=guild), "1")
    assert scaling == "medium"
    assert xp == 7
