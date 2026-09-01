from __future__ import annotations

from typing import Literal
from unittest.mock import AsyncMock, MagicMock

from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel

PermissionProfile = Literal[
    "admin",
    "member",
    "restricted",
    "no_guild",
    "channel_deny_send",
    "channel_deny_embed",
]

STANDARD_PERMISSION_PROFILES: tuple[PermissionProfile, ...] = (
    "admin",
    "member",
    "restricted",
    "no_guild",
    "channel_deny_send",
    "channel_deny_embed",
)

BASIC_PERMISSION_PROFILES: tuple[PermissionProfile, ...] = ("admin", "restricted")


def command_info_for_permission(
    profile: PermissionProfile,
    *,
    reply: AsyncMock | None = None,
) -> MagicMock:
    full = make_permissions(
        administrator=True,
        ban_members=True,
        kick_members=True,
        manage_roles=True,
        manage_messages=True,
        manage_guild=True,
        manage_channels=True,
        moderate_members=True,
        send_messages=True,
        embed_links=True,
        use_external_emojis=True,
    )
    member = make_permissions(
        administrator=False,
        ban_members=False,
        kick_members=False,
        manage_roles=False,
        manage_messages=False,
        manage_guild=False,
        manage_channels=False,
        moderate_members=False,
        send_messages=True,
        embed_links=True,
        use_external_emojis=True,
    )
    none = make_permissions(
        administrator=False,
        ban_members=False,
        kick_members=False,
        manage_roles=False,
        manage_messages=False,
        manage_guild=False,
        manage_channels=False,
        moderate_members=False,
        send_messages=False,
        embed_links=False,
        use_external_emojis=False,
    )
    deny_send = make_permissions(send_messages=False, embed_links=True)
    deny_embed = make_permissions(send_messages=True, embed_links=False)

    reply_mock = reply or AsyncMock()
    client = MagicMock()
    client.tree.walk_commands.return_value = []
    bot_user = MagicMock()
    bot_user.id = 999999999999999999
    client.user = bot_user
    client.fetch_user = AsyncMock(side_effect=lambda uid: make_member(user_id=int(uid)))

    if profile == "admin":
        user = make_member(top_role_position=50, guild_permissions=full)
        guild = make_guild(me_permissions=full, me_top_role_position=100)
        guild.get_member = MagicMock(side_effect=lambda uid: guild.me if int(uid) == bot_user.id else None)
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=full)
        return make_command_info(user=user, guild=guild, channel=channel, reply=reply_mock, client=client)

    if profile == "member":
        user = make_member(top_role_position=1, guild_permissions=member)
        guild = make_guild(me_permissions=full, me_top_role_position=100)
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=member)
        return make_command_info(user=user, guild=guild, channel=channel, reply=reply_mock, client=client)

    if profile == "restricted":
        user = make_member(top_role_position=1, guild_permissions=none)
        guild = make_guild(me_permissions=none)
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=none)
        return make_command_info(user=user, guild=guild, channel=channel, reply=reply_mock, client=client)

    if profile == "no_guild":
        user = make_member(top_role_position=1, guild_permissions=member)
        channel = make_text_channel()
        channel.guild = None
        channel.permissions_for = MagicMock(return_value=member)
        info = make_command_info(user=user, channel=channel, reply=reply_mock, client=client)
        info.guild = None
        return info

    if profile == "channel_deny_send":
        user = make_member(top_role_position=50, guild_permissions=full)
        guild = make_guild(me_permissions=full, me_top_role_position=100)
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=deny_send)
        return make_command_info(user=user, guild=guild, channel=channel, reply=reply_mock, client=client)

    if profile == "channel_deny_embed":
        user = make_member(top_role_position=50, guild_permissions=full)
        guild = make_guild(me_permissions=full, me_top_role_position=100)
        channel = make_text_channel(guild=guild)
        channel.permissions_for = MagicMock(return_value=deny_embed)
        return make_command_info(user=user, guild=guild, channel=channel, reply=reply_mock, client=client)

    raise ValueError(f"unknown permission profile: {profile}")
