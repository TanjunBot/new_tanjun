from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock


def make_guild(guild_id: int = 123456789, *, with_me: bool = True) -> MagicMock:
    guild = MagicMock()
    guild.id = guild_id
    guild.name = "Diagnostics Guild"
    guild.preferred_locale = "en-US"
    guild.get_member = MagicMock(return_value=None)
    guild.get_role = MagicMock(return_value=None)
    guild.get_channel = MagicMock(return_value=None)
    default_role = MagicMock()
    default_role.id = 222222222
    default_role.name = "@everyone"
    guild.default_role = default_role
    if with_me:
        me = MagicMock()
        me.id = 999999999
        me.guild_permissions = MagicMock(administrator=True)
        me.top_role = MagicMock(position=100)
        guild.me = me
    return guild


def make_member(
    user_id: int = 111111111,
    name: str = "TestUser",
    top_role_position: int = 50,
    guild: MagicMock | None = None,
) -> MagicMock:
    member = MagicMock()
    member.id = user_id
    member.name = name
    member.display_name = name
    member.mention = f"<@{user_id}>"
    member.top_role = MagicMock(position=top_role_position)
    member.guild_permissions = MagicMock(
        administrator=True,
        moderate_members=True,
        manage_messages=True,
        manage_channels=True,
    )
    member.bot = False
    member.send = AsyncMock()
    member.guild = guild or make_guild(with_me=False)
    return member


def make_text_channel(channel_id: int = 444444444, guild: MagicMock | None = None) -> MagicMock:
    channel = MagicMock()
    channel.id = channel_id
    channel.name = "diagnostics"
    channel.mention = f"<#{channel_id}>"
    channel.guild = guild or make_guild()
    channel.send = AsyncMock()
    channel.permissions_for = MagicMock(return_value=MagicMock(manage_messages=True, read_message_history=True))
    return channel


def make_choice(value: str) -> MagicMock:
    choice = MagicMock()
    choice.value = value
    return choice


def make_attachment() -> MagicMock:
    attachment = MagicMock()
    attachment.filename = "test.png"
    attachment.url = "https://example.com/test.png"
    attachment.read = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
    return attachment


def make_interaction(
    user: MagicMock | None = None,
    guild: MagicMock | None = None,
    channel: MagicMock | None = None,
    locale: str = "en-US",
) -> MagicMock:
    interaction = MagicMock()
    interaction.user = user or make_member()
    interaction.guild = guild or make_guild()
    interaction.channel = channel or make_text_channel(guild=interaction.guild)
    interaction.locale = locale
    interaction.command = MagicMock()
    interaction.message = None
    interaction.permissions = MagicMock()
    interaction.client = MagicMock()
    interaction.response = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.send_modal = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.original_response = AsyncMock(return_value=MagicMock())
    interaction.edit_original_response = AsyncMock()
    return interaction
