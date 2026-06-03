from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel
from tests.helpers.view_state import (
    assert_selection_marker,
    count_selection_markers,
    reply_description,
    view_from_reply,
)
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio

USER_IDS = ["111111111", "222222222", "333333333"]
CHANNEL_IDS = ["444444444", "555555555", "666666666"]
ROLE_IDS = ["777777777", "888888888", "999999999"]


def _admin_info():
    guild = make_guild()
    user = make_member()
    user.guild_permissions = make_permissions(administrator=True)
    channel = make_text_channel(guild=guild)
    return make_command_info(user=user, guild=guild, channel=channel)


def _make_view_interaction():
    interaction = make_view_interaction(make_member(guild_permissions=make_permissions(administrator=True)))
    interaction.response.edit_message = AsyncMock()
    return interaction


@pytest.mark.parametrize(
    "module_path,command_name,ids,remove_method,select_type,select_values",
    [
        (
            "commands.logs.blacklist_user.blacklist_list_user",
            "blacklist_list_user",
            USER_IDS,
            "remove_user",
            5,
            ["444444444"],
        ),
        (
            "commands.logs.blacklist_channel.blacklist_list_channel",
            "blacklist_list_channel",
            CHANNEL_IDS,
            "remove_channel",
            8,
            ["101010101"],
        ),
        (
            "commands.logs.blacklist_role.blacklist_list_role",
            "blacklist_list_role",
            ROLE_IDS,
            "remove_role",
            6,
            ["121212121"],
        ),
    ],
)
async def test_blacklist_list_initial_marker_on_first_entry(
    module_path,
    command_name,
    ids,
    remove_method,
    select_type,
    select_values,
):
    import importlib

    mod = importlib.import_module(module_path)
    info = _admin_info()
    handler = getattr(mod, command_name)
    with patch.object(mod, "get_log_blacklist", new=AsyncMock(return_value=ids)):
        await handler(info)
    desc = reply_description(info)
    assert_selection_marker(desc)
    assert count_selection_markers(desc) == 1
    first_id = ids[0]
    assert f"<@{first_id}>" in desc or f"<#{first_id}>" in desc or first_id in desc
    view = view_from_reply(info)
    selected = getattr(view, "selected_index", getattr(view, "selectedIndex", None))
    assert selected == 0


@pytest.mark.parametrize(
    "module_path,command_name,ids,nav_method",
    [
        ("commands.logs.blacklist_user.blacklist_list_user", "blacklist_list_user", USER_IDS, "down"),
        ("commands.logs.blacklist_channel.blacklist_list_channel", "blacklist_list_channel", CHANNEL_IDS, "down"),
        ("commands.logs.blacklist_role.blacklist_list_role", "blacklist_list_role", ROLE_IDS, "down"),
    ],
)
async def test_blacklist_list_down_moves_marker(module_path, command_name, ids, nav_method):
    import importlib

    mod = importlib.import_module(module_path)
    info = _admin_info()
    with patch.object(mod, "get_log_blacklist", new=AsyncMock(return_value=ids)):
        await getattr(mod, command_name)(info)
    view = view_from_reply(info)
    interaction = _make_view_interaction()
    await getattr(view, nav_method)(interaction, MagicMock())
    desc = interaction.response.edit_message.await_args.kwargs["embed"].description or ""
    assert count_selection_markers(desc) == 1
    selected = getattr(view, "selected_index", getattr(view, "selectedIndex", None))
    assert selected == 1


@pytest.mark.parametrize(
    "module_path,command_name,ids",
    [
        ("commands.logs.blacklist_user.blacklist_list_user", "blacklist_list_user", USER_IDS),
        ("commands.logs.blacklist_channel.blacklist_list_channel", "blacklist_list_channel", CHANNEL_IDS),
        ("commands.logs.blacklist_role.blacklist_list_role", "blacklist_list_role", ROLE_IDS),
    ],
)
async def test_blacklist_list_up_wraps_from_first(module_path, command_name, ids):
    import importlib

    mod = importlib.import_module(module_path)
    info = _admin_info()
    with patch.object(mod, "get_log_blacklist", new=AsyncMock(return_value=ids)):
        await getattr(mod, command_name)(info)
    view = view_from_reply(info)
    interaction = _make_view_interaction()
    await view.up(interaction, MagicMock())
    selected = getattr(view, "selected_index", getattr(view, "selectedIndex", None))
    assert selected == len(ids) - 1


@pytest.mark.parametrize(
    "module_path,command_name",
    [
        ("commands.logs.blacklist_user.blacklist_list_user", "blacklist_list_user"),
        ("commands.logs.blacklist_channel.blacklist_list_channel", "blacklist_list_channel"),
        ("commands.logs.blacklist_role.blacklist_list_role", "blacklist_list_role"),
    ],
)
async def test_blacklist_list_empty_no_marker(module_path, command_name):
    import importlib

    mod = importlib.import_module(module_path)
    info = _admin_info()
    with patch.object(mod, "get_log_blacklist", new=AsyncMock(return_value=[])):
        await getattr(mod, command_name)(info)
    desc = reply_description(info)
    assert_selection_marker(desc, present=False)
    view = view_from_reply(info)
    entries = getattr(view, "users", None) or getattr(view, "channels", None) or getattr(view, "roles", None)
    assert not entries
