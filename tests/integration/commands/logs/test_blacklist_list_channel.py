from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel

pytestmark = pytest.mark.asyncio


def _admin_info():
    guild = make_guild()
    user = make_member()
    user.guild_permissions = make_permissions(administrator=True)
    channel = make_text_channel(guild=guild)
    return make_command_info(user=user, guild=guild, channel=channel)


def _restricted_info():
    guild = make_guild()
    user = make_member()
    user.guild_permissions = make_permissions(administrator=False)
    channel = make_text_channel(guild=guild)
    return make_command_info(user=user, guild=guild, channel=channel)


@patch("commands.logs.blacklist_channel.blacklist_list_channel.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_channel_missing_permission(mock_get):
    from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel

    info = _restricted_info()
    await blacklist_list_channel(info)
    info.reply.assert_awaited_once()
    mock_get.assert_not_called()


@patch("commands.logs.blacklist_channel.blacklist_list_channel.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_channel_empty(mock_get):
    from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel

    mock_get.return_value = []
    info = _admin_info()
    await blacklist_list_channel(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("view") is not None


@patch("commands.logs.blacklist_channel.blacklist_list_channel.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_channel_with_entries(mock_get):
    from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel

    mock_get.return_value = ["444444444", "555555555"]
    info = _admin_info()
    await blacklist_list_channel(info)
    info.reply.assert_awaited_once()


@patch("commands.logs.blacklist_channel.blacklist_list_channel.remove_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_channel.blacklist_list_channel.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_channel_remove_button(mock_get, mock_remove):
    from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel

    mock_get.return_value = ["444444444"]
    info = _admin_info()
    await blacklist_list_channel(info)
    view = info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()
    await view.remove_channel(interaction, MagicMock())
    mock_remove.assert_awaited_once()


@patch("commands.logs.blacklist_channel.blacklist_list_channel.add_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_channel.blacklist_list_channel.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_channel_add_via_select(mock_get, mock_add):
    from commands.logs.blacklist_channel.blacklist_list_channel import blacklist_list_channel

    mock_get.return_value = []
    info = _admin_info()
    await blacklist_list_channel(info)
    view = info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.data = {"component_type": 8, "values": ["666666666"]}
    interaction.response.edit_message = AsyncMock()
    await view.interaction_check(interaction)
    mock_add.assert_awaited_once()
