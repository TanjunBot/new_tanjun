import pytest
from unittest.mock import AsyncMock, MagicMock

from commands.admin.copyrole import copyrole
from tests.helpers.discord import make_permissions, make_role, make_target_member


pytestmark = pytest.mark.asyncio


async def test_copyrole_missing_user_permission(restricted_command_info):
    role = make_role()
    await copyrole(restricted_command_info, role=role)
    restricted_command_info.reply.assert_awaited_once()


async def test_copyrole_missing_bot_permission(admin_command_info):
    guild = admin_command_info.guild
    guild.me.guild_permissions = make_permissions(manage_roles=False)
    guild.get_member = MagicMock(return_value=guild.me)
    admin_command_info.client.user = MagicMock(id=guild.me.id)
    role = make_role()
    await copyrole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


def _setup_source_role(role):
    role.icon = None
    role.unicode_emoji = None
    role.color = MagicMock()
    role.permissions = MagicMock()
    role.hoist = False
    role.mentionable = False
    role.members = []


async def test_copyrole_success(admin_command_info):
    role = make_role()
    _setup_source_role(role)
    new_role = make_role()
    new_role.edit = AsyncMock()
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await copyrole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()
    new_role.edit.assert_awaited_once()


async def test_copyrole_success_with_members(admin_command_info):
    role = make_role()
    _setup_source_role(role)
    role.members = [make_target_member()]
    new_role = make_role()
    new_role.edit = AsyncMock()
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await copyrole(admin_command_info, role=role, copy_members=True)
    role.members[0].add_roles.assert_awaited_once_with(new_role)


async def test_copyrole_with_icon(admin_command_info):
    role = make_role()
    _setup_source_role(role)
    icon = MagicMock()
    icon.read = AsyncMock(return_value=b"bytes")
    role.icon = icon
    new_role = make_role()
    new_role.edit = AsyncMock()
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await copyrole(admin_command_info, role=role)
    admin_command_info.reply.assert_awaited_once()


async def test_copyrole_with_unicode_emoji(admin_command_info):
    role = make_role()
    _setup_source_role(role)
    role.unicode_emoji = "🎭"
    new_role = make_role()
    new_role.edit = AsyncMock()
    admin_command_info.client.user = MagicMock(id=admin_command_info.guild.me.id)
    admin_command_info.guild.get_member = MagicMock(return_value=admin_command_info.guild.me)
    admin_command_info.guild.create_role = AsyncMock(return_value=new_role)
    await copyrole(admin_command_info, role=role)
    admin_command_info.guild.create_role.assert_awaited_once()
