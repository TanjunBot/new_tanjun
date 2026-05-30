import io
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import discord

from commands.level.change_xp_scaling import change_xp_scaling_command
from commands.level.disable_level_system import disable_level_system
from commands.level.leaderboard import leaderboard
from commands.level.level_blacklist import (
    add_channel_to_blacklist_command,
    add_role_to_blacklist_command,
    add_user_to_blacklist_command,
    remove_channel_from_blacklist_command,
    remove_role_from_blacklist_command,
    remove_user_from_blacklist_command,
    show_blacklist_command,
)
from commands.level.level_boosts import (
    add_channel_boost_command,
    add_role_boost_command,
    add_user_boost_command,
    calculate_user_channel_boost_command,
    remove_channel_boost_command,
    remove_role_boost_command,
    remove_user_boost_command,
    show_boosts_command,
)
from commands.level.level_rankcard import generate_rankcard, set_background_command, show_rankcard_command
from commands.level.level_set_xp_cooldown import set_text_cooldown_command, set_voice_cooldown_command
from commands.level.show_level_roles import show_level_roles_command
from tests.helpers.discord import make_role, make_target_member, make_text_channel
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


@patch("commands.level.change_xp_scaling.set_custom_formula", new_callable=AsyncMock)
@patch("commands.level.change_xp_scaling.set_xp_scaling", new_callable=AsyncMock)
@patch("commands.level.change_xp_scaling.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_change_xp_scaling_custom(mock_xp, mock_set, mock_formula, admin_command_info):
    await change_xp_scaling_command(admin_command_info, "custom", custom_formula="level*100")
    mock_formula.assert_awaited_once()


async def test_change_xp_scaling_invalid(admin_command_info):
    await change_xp_scaling_command(admin_command_info, "invalid_scaling")
    admin_command_info.reply.assert_awaited_once()


async def test_change_xp_scaling_custom_no_formula(admin_command_info):
    await change_xp_scaling_command(admin_command_info, "custom")
    admin_command_info.reply.assert_awaited_once()


async def test_change_xp_scaling_no_permission(restricted_command_info):
    from unittest.mock import MagicMock
    restricted_command_info.user.guild_permissions = MagicMock(administrator=False)
    await change_xp_scaling_command(restricted_command_info, "medium")
    restricted_command_info.reply.assert_awaited_once()


@patch("commands.level.change_xp_scaling.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.change_xp_scaling.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_show_xp_scalings(mock_xp, mock_formula, admin_command_info):
    from commands.level.change_xp_scaling import show_xp_scalings

    await show_xp_scalings(admin_command_info, start_level=1, end_level=20)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.level.change_xp_scaling.set_xp_scaling", new_callable=AsyncMock)
@pytest.mark.parametrize("scaling", ["easy", "medium", "hard", "extreme"])
async def test_change_xp_scaling_values(mock_set, admin_command_info, scaling):
    await change_xp_scaling_command(admin_command_info, scaling)
    mock_set.assert_awaited_once()


@patch("commands.level.disable_level_system.get_level_system_status", new_callable=AsyncMock, return_value=True)
async def test_disable_level_system_shows_confirm(mock_status, admin_command_info):
    await disable_level_system(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    assert admin_command_info.reply.await_args.kwargs.get("view") is not None


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=25)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock)
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=5)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_paginator_previous(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
    entry = MagicMock(user_id="111", xp=500)
    mock_page.return_value = [entry]
    await leaderboard(admin_command_info, page=2)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.previous(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=25)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_paginator_next(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
    await leaderboard(admin_command_info, page=1)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.next(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


@patch("commands.level.leaderboard.get_level_leaderboard_count", new_callable=AsyncMock, return_value=25)
@patch("commands.level.leaderboard.get_xp_scaling", new_callable=AsyncMock, return_value="medium")
@patch("commands.level.leaderboard.get_custom_formula", new_callable=AsyncMock, return_value=None)
@patch("commands.level.leaderboard.get_level_leaderboard_paginated", new_callable=AsyncMock, return_value=[])
@patch("commands.level.leaderboard.get_level_for_xp_async", new_callable=AsyncMock, return_value=1)
@patch("commands.level.leaderboard.get_xp_for_level_async", new_callable=AsyncMock, return_value=100)
async def test_leaderboard_unauthorized(mock_xp, mock_level, mock_page, mock_formula, mock_scaling, mock_count, admin_command_info):
    await leaderboard(admin_command_info, page=1)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=make_target_member(user_id=999))
    await view.previous(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


@patch("commands.level.level_blacklist.add_user_to_blacklist", new_callable=AsyncMock)
async def test_add_user_blacklist(mock_add, admin_command_info):
    user = make_target_member()
    await add_user_to_blacklist_command(admin_command_info, user, reason="spam")
    mock_add.assert_awaited_once()


@patch("commands.level.level_blacklist.add_role_to_blacklist", new_callable=AsyncMock)
async def test_add_role_blacklist(mock_add, admin_command_info):
    role = make_role()
    await add_role_to_blacklist_command(admin_command_info, role)
    mock_add.assert_awaited_once()


@patch("commands.level.level_blacklist.add_channel_to_blacklist", new_callable=AsyncMock)
async def test_add_channel_blacklist(mock_add, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await add_channel_to_blacklist_command(admin_command_info, channel)
    mock_add.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_user_from_blacklist", new_callable=AsyncMock)
async def test_remove_user_blacklist(mock_remove, admin_command_info):
    user = make_target_member()
    await remove_user_from_blacklist_command(admin_command_info, user)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_role_from_blacklist", new_callable=AsyncMock)
async def test_remove_role_blacklist(mock_remove, admin_command_info):
    role = make_role()
    await remove_role_from_blacklist_command(admin_command_info, role)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.remove_channel_from_blacklist", new_callable=AsyncMock)
async def test_remove_channel_blacklist(mock_remove, admin_command_info):
    channel = make_text_channel(guild=admin_command_info.guild)
    await remove_channel_from_blacklist_command(admin_command_info, channel)
    mock_remove.assert_awaited_once()


@patch("commands.level.level_blacklist.get_blacklist", new_callable=AsyncMock)
async def test_show_blacklist(mock_get, admin_command_info):
    mock_get.return_value = {
        "channels": [("111", "reason")],
        "roles": [("222", None)],
        "users": [("333", "test")],
    }
    await show_blacklist_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_boosts.get_user_boost", new_callable=AsyncMock, return_value=(2.0, True))
@patch("commands.level.level_boosts.get_user_roles_boosts", new_callable=AsyncMock, return_value=[(1.5, False)])
@patch("commands.level.level_boosts.get_channel_boost", new_callable=AsyncMock, return_value=(1.2, False))
async def test_calculate_user_channel_boost(mock_ch, mock_roles, mock_user, admin_command_info):
    user = make_target_member()
    user.roles = [make_role()]
    channel = make_text_channel(guild=admin_command_info.guild)
    await calculate_user_channel_boost_command(admin_command_info, user, channel)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_boosts.add_role_boost", new_callable=AsyncMock)
@pytest.mark.parametrize("additive", [True, False])
async def test_add_role_boost_additive(mock_add, admin_command_info, additive):
    role = make_role()
    await add_role_boost_command(admin_command_info, role, 2.0, additive)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.add_channel_boost", new_callable=AsyncMock)
@pytest.mark.parametrize("additive", [True, False])
async def test_add_channel_boost_additive(mock_add, admin_command_info, additive):
    channel = make_text_channel(guild=admin_command_info.guild)
    await add_channel_boost_command(admin_command_info, channel, 1.5, additive)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.add_user_boost", new_callable=AsyncMock)
@pytest.mark.parametrize("additive", [True, False])
async def test_add_user_boost_additive(mock_add, admin_command_info, additive):
    user = make_target_member()
    await add_user_boost_command(admin_command_info, user, 2.0, additive)
    mock_add.assert_awaited_once()


@patch("commands.level.level_boosts.remove_role_boost", new_callable=AsyncMock)
async def test_remove_role_boost(mock_remove, admin_command_info):
    await remove_role_boost_command(admin_command_info, make_role())
    mock_remove.assert_awaited_once()


@patch("commands.level.level_boosts.remove_channel_boost", new_callable=AsyncMock)
async def test_remove_channel_boost(mock_remove, admin_command_info):
    await remove_channel_boost_command(admin_command_info, make_text_channel(guild=admin_command_info.guild))
    mock_remove.assert_awaited_once()


@patch("commands.level.level_boosts.remove_user_boost", new_callable=AsyncMock)
async def test_remove_user_boost(mock_remove, admin_command_info):
    await remove_user_boost_command(admin_command_info, make_target_member())
    mock_remove.assert_awaited_once()


@patch("commands.level.level_boosts.get_all_boosts", new_callable=AsyncMock)
async def test_show_boosts_with_data(mock_get, admin_command_info):
    mock_get.return_value = {
        "roles": [("1", 2.0, True)],
        "channels": [("2", 1.5, False)],
        "users": [("3", 3.0, True)],
    }
    await show_boosts_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_rankcard.get_image_or_gif_frames", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.run_in_executor", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.get_user_level_info", new_callable=AsyncMock)
async def test_generate_rankcard_custom_bg(mock_info, mock_exec, mock_frames, admin_command_info):
    from PIL import Image

    user = make_target_member()
    user_info = MagicMock(custom_background="http://example.com/bg.png")
    mock_frames.return_value = ([Image.new("RGBA", (10, 10))], 100)
    mock_exec.return_value = io.BytesIO(b"gif")
    result = await generate_rankcard(user, user_info, admin_command_info)
    assert isinstance(result, io.BytesIO)


@patch("commands.level.level_rankcard.get_image_or_gif_frames", new_callable=AsyncMock, return_value=([], 0))
@patch("commands.level.level_rankcard.get_user_level_info", new_callable=AsyncMock)
async def test_generate_rankcard_empty_avatar(mock_info, mock_frames, admin_command_info):
    user = make_target_member()
    user_info = MagicMock(custom_background=None)
    mock_info.return_value = user_info
    result = await generate_rankcard(user, user_info, admin_command_info)
    assert isinstance(result, io.BytesIO)


@patch("commands.level.level_set_xp_cooldown.set_text_cooldown", new_callable=AsyncMock)
async def test_set_text_cooldown(mock_set, admin_command_info):
    await set_text_cooldown_command(admin_command_info, 60)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_set_xp_cooldown.set_voice_cooldown", new_callable=AsyncMock)
async def test_set_voice_cooldown(mock_set, admin_command_info):
    await set_voice_cooldown_command(admin_command_info, 30)
    mock_set.assert_awaited_once()
    admin_command_info.reply.assert_awaited_once()


async def test_set_text_cooldown_invalid(admin_command_info):
    await set_text_cooldown_command(admin_command_info, -1)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock)
async def test_show_level_roles_with_pagination(mock_get, admin_command_info):
    groups = [MagicMock(level=i, role_ids=[str(i)]) for i in range(30)]
    mock_get.return_value = groups
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()
    view = admin_command_info.reply.await_args.kwargs["view"]
    assert view is not None


@patch("commands.level.show_level_roles.get_all_level_roles", new_callable=AsyncMock, return_value=[])
async def test_show_level_roles_empty(mock_get, admin_command_info):
    await show_level_roles_command(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


@patch("commands.level.level_rankcard.upload_image_to_imgbb", new_callable=AsyncMock)
@patch("commands.level.level_rankcard.set_custom_background", new_callable=AsyncMock)
async def test_set_background_gif(mock_set, mock_upload, admin_command_info):
    image = MagicMock()
    image.content_type = "image/gif"
    image.read = AsyncMock(return_value=b"gifdata")
    mock_upload.return_value = {"data": {"url": "http://example.com/bg.gif"}}
    await set_background_command(admin_command_info, image)
    mock_set.assert_awaited_once()
