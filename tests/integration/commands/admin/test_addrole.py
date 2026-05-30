import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.admin.addrole import addrole
from tests.helpers.discord import make_permissions, make_role, make_target_member
from tests.integration.commands.admin.conftest import make_view_interaction


pytestmark = pytest.mark.asyncio


async def test_addrole_missing_permission(restricted_command_info):
    await addrole(restricted_command_info)
    restricted_command_info.reply.assert_awaited_once()


async def test_addrole_missing_bot_permission(admin_command_info):
    admin_command_info.guild.me.guild_permissions = make_permissions(manage_roles=False)
    await addrole(admin_command_info)
    admin_command_info.reply.assert_awaited_once()


async def test_addrole_shows_view_without_args(admin_command_info):
    await addrole(admin_command_info)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("view") is not None


async def test_addrole_already_has_role(admin_command_info):
    user = make_target_member()
    role = make_role(position=5)
    user.roles = [role]
    await addrole(admin_command_info, user, role)
    admin_command_info.reply.assert_awaited_once()


async def test_addrole_role_too_high(admin_command_info):
    user = make_target_member()
    role = make_role(position=100)
    admin_command_info.user.top_role = make_role(position=10)
    await addrole(admin_command_info, user, role)
    admin_command_info.reply.assert_awaited_once()


async def test_addrole_success(admin_command_info):
    user = make_target_member()
    role = make_role(position=5)
    user.roles = []
    await addrole(admin_command_info, user, role)
    user.add_roles.assert_awaited_once_with(role)
    admin_command_info.reply.assert_awaited_once()


async def test_addrole_bot_role_too_high(admin_command_info):
    user = make_target_member()
    role = make_role(position=200)
    admin_command_info.guild.me.top_role = make_role(position=10)
    user.roles = []
    await addrole(admin_command_info, user, role)
    admin_command_info.reply.assert_awaited_once()


async def test_addrole_view_confirm_no_selection(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    view.selected_roles = []
    view.selected_users = []
    await view.confirm(interaction, MagicMock())
    interaction.response.send_message.assert_awaited_once()


async def test_addrole_view_confirm_add_roles(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    user = make_target_member()
    role = make_role(position=5)
    user.roles = []
    view.selected_users = [user]
    view.selected_roles = [role]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.confirm(interaction, MagicMock())
    user.add_roles.assert_awaited_once_with(role)
    interaction.response.edit_message.assert_awaited_once()


async def test_addrole_view_confirm_remove_existing(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    view.action = "remove"
    user = make_target_member()
    role = make_role(position=5)
    user.roles = [role]
    view.selected_users = [user]
    view.selected_roles = [role]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.confirm(interaction, MagicMock())
    user.remove_roles.assert_awaited_once_with(role)


async def test_addrole_view_cancel(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.response.edit_message = AsyncMock()
    await view.cancel(interaction, MagicMock())
    interaction.response.edit_message.assert_awaited_once()


async def test_addrole_view_interaction_check_role_select(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    role = make_role(role_id=555555555)
    admin_command_info.guild.get_role = MagicMock(return_value=role)
    interaction = make_view_interaction(user=admin_command_info.user, guild=admin_command_info.guild)
    interaction.data = {"component_type": 6, "values": ["555555555"]}
    result = await view.interaction_check(interaction)
    assert result is True
    assert role in view.selected_roles
    interaction.response.defer.assert_awaited_once()


async def test_addrole_view_interaction_check_user_select(admin_command_info):
    await addrole(admin_command_info)
    view = admin_command_info.reply.await_args.kwargs["view"]
    member = make_target_member(user_id=222222222)
    admin_command_info.guild.fetch_member = AsyncMock(return_value=member)
    interaction = make_view_interaction(user=admin_command_info.user, guild=admin_command_info.guild)
    interaction.data = {"component_type": 5, "values": ["222222222"]}
    result = await view.interaction_check(interaction)
    assert result is True
    assert member in view.selected_users


async def test_addrole_with_user_only(admin_command_info):
    user = make_target_member()
    await addrole(admin_command_info, user=user)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("view") is not None


async def test_addrole_with_role_only(admin_command_info):
    role = make_role(position=5)
    await addrole(admin_command_info, role=role)
    call = admin_command_info.reply.await_args
    assert call.kwargs.get("view") is not None
