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


@patch("commands.logs.blacklist_user.blacklist_list_user.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_user_missing_permission(mock_get):
    from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user

    info = _restricted_info()
    await blacklist_list_user(info)
    info.reply.assert_awaited_once()
    mock_get.assert_not_called()


@patch("commands.logs.blacklist_user.blacklist_list_user.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_user_empty(mock_get):
    from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user

    mock_get.return_value = []
    info = _admin_info()
    await blacklist_list_user(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("view") is not None


@patch("commands.logs.blacklist_user.blacklist_list_user.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_user_with_entries(mock_get):
    from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user

    mock_get.return_value = ["111111111", "222222222"]
    info = _admin_info()
    await blacklist_list_user(info)
    info.reply.assert_awaited_once()
    assert info.reply.await_args.kwargs.get("embed") is not None


@patch("commands.logs.blacklist_user.blacklist_list_user.remove_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_user.blacklist_list_user.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_user_remove_button(mock_get, mock_remove):
    from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user

    mock_get.return_value = ["111111111"]
    info = _admin_info()
    await blacklist_list_user(info)
    view = info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.response.edit_message = AsyncMock()
    await view.remove_user(interaction, MagicMock())
    mock_remove.assert_awaited_once()


@patch("commands.logs.blacklist_user.blacklist_list_user.add_log_blacklist", new_callable=AsyncMock)
@patch("commands.logs.blacklist_user.blacklist_list_user.get_log_blacklist", new_callable=AsyncMock)
async def test_blacklist_list_user_add_via_select(mock_get, mock_add):
    from commands.logs.blacklist_user.blacklist_list_user import blacklist_list_user

    mock_get.return_value = []
    info = _admin_info()
    await blacklist_list_user(info)
    view = info.reply.await_args.kwargs["view"]
    interaction = MagicMock()
    interaction.data = {"component_type": 5, "values": ["333333333"]}
    interaction.response.edit_message = AsyncMock()
    await view.interaction_check(interaction)
    mock_add.assert_awaited_once()
