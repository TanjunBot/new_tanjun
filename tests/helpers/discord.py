from __future__ import annotations
from locale_keys import locale
import sys
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from tests.helpers.discord_exceptions import FakeEmbed, Forbidden, HTTPException, NotFound
_discord = sys.modules.get('discord')
if _discord is None:
    _discord = MagicMock()
    sys.modules['discord'] = _discord

class MockMember(MagicMock):
    pass
MockMember.__name__ = 'Member'

class MockGuild(MagicMock):
    pass

class MockTextChannel(MockGuild):
    pass

class MockRole:

    def __init__(self, position: int=0, role_id: int=555555555555555555, name: str='TestRole') -> None:
        self.position = position
        self.id = role_id
        self.name = name
        self.mention = f'<@&{role_id}>'
        self.edit = AsyncMock()
        self.permissions = MagicMock(administrator=False, manage_roles=True)

    def __ge__(self, other: object) -> bool:
        if isinstance(other, MockRole):
            return self.position >= other.position
        if hasattr(other, 'position'):
            return self.position >= other.position
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, MockRole):
            return self.position <= other.position
        if hasattr(other, 'position'):
            return self.position <= other.position
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, MockRole):
            return self.position > other.position
        if hasattr(other, 'position'):
            return self.position > other.position
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, MockRole):
            return self.position < other.position
        if hasattr(other, 'position'):
            return self.position < other.position
        return NotImplemented

class MockVoiceChannel(MockGuild):
    pass

class MockView:

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.timeout = kwargs.get('timeout')
        self.children: list[Any] = []
        self.message = None

    def add_item(self, item: Any) -> None:
        self.children.append(item)

    async def wait(self) -> bool:
        return True

    def stop(self) -> None:
        pass

    def clear_items(self) -> None:
        self.children.clear()

class MockModal(MockView):

    def __init__(self, *args: Any, title: str='', **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.title = title

    def __init_subclass__(cls, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(cls, key, value)

class _UIButtonDescriptor:

    def __init__(self, func: Any, **kwargs: Any) -> None:
        self.callback = func
        self.disabled = False
        self.label = kwargs.get('label', '')
        self.style = kwargs.get('style')
        self.emoji = kwargs.get('emoji')
        self.row = kwargs.get('row')
        self.custom_id = kwargs.get('custom_id')
        self._view: Any = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, owner: type | None=None) -> _UIButtonDescriptor:
        self._view = obj
        return self

    async def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._view is not None:
            return await self.callback(self._view, *args, **kwargs)
        return await self.callback(*args, **kwargs)

def _ui_button(*args: Any, **kwargs: Any) -> Callable[[Any], _UIButtonDescriptor]:

    def decorator(func: Any) -> _UIButtonDescriptor:
        return _UIButtonDescriptor(func, **kwargs)
    return decorator

def _mock_discord_get(iterable: Any, **attrs: Any) -> Any:
    items = list(iterable) if iterable is not None else []
    for item in items:
        match = True
        for key, expected in attrs.items():
            if '__' in key:
                obj_name, attr_name = key.split('__', 1)
                obj = getattr(item, obj_name, None)
                if getattr(obj, attr_name, None) != expected:
                    match = False
                    break
            elif getattr(item, key, None) != expected:
                match = False
                break
        if match:
            return item
    return None

def _ui_item(cls: type) -> type:

    class _Item:

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.label = kwargs.get('label', '')
            self.placeholder = kwargs.get('placeholder', '')
            self.default = kwargs.get('default', '')
            self.required = kwargs.get('required', False)
            self.value = self.default
            self.custom_id = kwargs.get('custom_id', '')
            self.disabled = False

        @classmethod
        def __class_getitem__(cls, item: Any) -> type:
            return cls
    _Item.__name__ = cls.__name__
    return _Item

class MockColor:

    def __init__(self, value: int=0) -> None:
        self.value = value

    @staticmethod
    def default() -> MockColor:
        return MockColor(0)

class MockAttachment:
    pass

def _ensure_discord_types() -> None:
    import discord
    discord.Member = MockMember
    discord.Guild = MockGuild
    discord.TextChannel = MockTextChannel
    discord.Role = MockRole
    discord.VoiceChannel = MockVoiceChannel
    if not hasattr(discord, 'abc') or discord.abc is None:
        discord.abc = MagicMock()
    discord.abc.GuildChannel = MockGuild
    discord.Forbidden = Forbidden
    discord.HTTPException = HTTPException
    discord.NotFound = NotFound
    discord.Embed = FakeEmbed
    if not hasattr(discord, 'utils') or discord.utils is None:
        discord.utils = MagicMock()
    discord.utils.utcnow = lambda: datetime.now(UTC)
    discord.utils.get = _mock_discord_get
    if not hasattr(discord, 'ui') or discord.ui is None:
        discord.ui = MagicMock()
    discord.ui.View = MockView
    discord.ui.Modal = MockModal
    discord.ui.button = _ui_button
    discord.ui.Select = _ui_item(type('Select', (), {}))
    discord.ui.TextInput = _ui_item(type('TextInput', (), {}))
    discord.ui.RoleSelect = _ui_item(type('RoleSelect', (), {}))
    discord.ui.UserSelect = _ui_item(type('UserSelect', (), {}))
    discord.ui.Button = _ui_item(type('Button', (), {}))
    discord.Attachment = MockAttachment
    discord.Color = MockColor
    discord.Thread = type('Thread', (), {})
_ensure_discord_types()

def make_member(user_id: int=111111111111111111, name: str='TestUser', top_role_position: int=1, guild_permissions: MagicMock | None=None) -> MockMember:
    member = MockMember()
    member.id = user_id
    member.name = name
    member.display_name = name
    member.mention = f'<@{user_id}>'
    member.top_role = MockRole(position=top_role_position)
    member.guild_permissions = guild_permissions or MagicMock()
    member.ban = AsyncMock()
    member.kick = AsyncMock()
    member.edit = AsyncMock()
    member.add_roles = AsyncMock()
    member.remove_roles = AsyncMock()
    member.timeout = AsyncMock()
    member.move_to = AsyncMock()
    member.bot = False
    member.is_timed_out = MagicMock(return_value=False)
    member.send = AsyncMock()
    member.display_avatar = MagicMock(url='https://cdn.discordapp.com/embed/avatars/0.png')
    member.guild_avatar = None
    member.avatar = None
    member.banner = None
    member.guild = make_guild()
    member.create_dm = AsyncMock(return_value=MagicMock())
    return member

def make_guild(guild_id: int=123456789012345678, me_permissions: MagicMock | None=None, me_top_role_position: int=100) -> MockGuild:
    guild = MockGuild()
    guild.id = guild_id
    guild.name = 'Test Guild'
    guild.preferred_locale = 'en-US'
    guild.edit = AsyncMock()
    guild.fetch_member = AsyncMock(side_effect=lambda _uid: make_member())
    guild.create_custom_emoji = AsyncMock(return_value=MagicMock())
    guild.create_role = AsyncMock(return_value=MockRole(position=1))
    guild.unban = AsyncMock()
    me = MockMember()
    me.guild_permissions = me_permissions or MagicMock()
    me.top_role = MockRole(position=me_top_role_position)
    guild.me = me
    guild.get_member = MagicMock(return_value=None)
    guild.get_role = MagicMock(return_value=None)
    guild.get_channel = MagicMock(return_value=None)
    guild.default_role = MagicMock()
    guild.default_role.id = 111
    return guild

def make_text_channel(channel_id: int=444444444444444444, guild: MagicMock | None=None) -> MockTextChannel:
    channel = MockTextChannel()
    channel.id = channel_id
    channel.name = 'test-channel'
    channel.mention = f'<#{channel_id}>'
    channel.guild = guild or make_guild()
    channel.send = AsyncMock()
    channel.purge = AsyncMock(return_value=[])
    channel.set_permissions = AsyncMock()
    channel.edit = AsyncMock()
    channel.clone = AsyncMock(return_value=channel)
    channel.delete = AsyncMock()
    channel.permissions_for = MagicMock(return_value=MagicMock())
    thread = MagicMock()
    thread.send = AsyncMock(return_value=MagicMock(edit=AsyncMock()))
    channel.create_thread = AsyncMock(return_value=thread)
    return channel

def make_app_command_channel(
    channel_id: int=444444444444444444,
    guild: MagicMock | None=None,
    *,
    resolved: MockTextChannel | MagicMock | None=None,
    fetch_raises: type[BaseException] | None=None,
) -> MagicMock:
    guild = guild or make_guild()
    selected = MagicMock(spec=['id', 'name', 'mention', 'guild_id', 'permissions', 'resolve', 'fetch'])
    selected.id = channel_id
    selected.name = 'test-channel'
    selected.mention = f'<#{channel_id}>'
    selected.guild_id = guild.id
    selected.permissions = make_permissions(send_messages=True, view_channel=True)
    selected.resolve = MagicMock(return_value=resolved)
    if fetch_raises is not None:
        selected.fetch = AsyncMock(side_effect=fetch_raises())
    else:
        selected.fetch = AsyncMock(return_value=resolved)
    return selected

def make_command_info(user: MagicMock | None=None, guild: MagicMock | None=None, channel: MagicMock | None=None, locale: str='en-US', reply: AsyncMock | None=None, client: MagicMock | None=None, **kwargs: Any) -> CommandInfo:
    from utility import CommandInfo
    user = user or make_member()
    guild = guild or make_guild()
    channel = channel or make_text_channel(guild=guild)
    reply_mock = reply or AsyncMock()
    info = CommandInfo(user=user, guild=guild, channel=channel, locale=locale, client=client or MagicMock(), command=MagicMock(), message=None, permissions=kwargs.pop('permissions', MagicMock()), **kwargs)
    info.reply = reply_mock
    return info

def make_interaction(user: MagicMock | None=None, guild: MagicMock | None=None, channel: MagicMock | None=None, locale: str='en-US') -> MagicMock:
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
    interaction.response.send_modal = MagicMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    interaction.edit_original_response = AsyncMock()
    return interaction

def make_message(content: str='test', author: MagicMock | None=None, guild: MagicMock | None=None, channel: MagicMock | None=None) -> MagicMock:
    message = MagicMock()
    message.content = content
    message.author = author or make_member()
    message.guild = guild or make_guild()
    message.channel = channel or make_text_channel(guild=message.guild)
    message.id = 999999999
    message.reply = AsyncMock()
    return message

def assert_embed_error(embed: MagicMock) -> None:
    from utility import EmbedColor
    assert embed.colour == EmbedColor.ERROR or getattr(embed, 'color', None) == EmbedColor.ERROR

def assert_embed_success(embed: MagicMock) -> None:
    from utility import EmbedColor
    assert embed.colour == EmbedColor.SUCCESS or getattr(embed, 'color', None) == EmbedColor.SUCCESS

def make_permissions(**flags: bool) -> MagicMock:
    perms = MagicMock()
    for key, value in flags.items():
        setattr(perms, key, value)
    return perms

def make_role(role_id: int=555555555, name: str='TestRole', position: int=5, mention: str | None=None) -> MockRole:
    role = MockRole(position=position, role_id=role_id, name=name)
    if mention:
        role.mention = mention
    return role

def make_target_member(user_id: int=222222222, name: str='TargetUser', top_role_position: int=1) -> MockMember:
    target = make_member(user_id=user_id, name=name, top_role_position=top_role_position)
    target.roles = []
    return target

def make_warn_config(expiration_days: int=30, max_warnings: int=3, ban_threshold: int=10, kick_threshold: int=5, timeout_threshold: int=2, timeout_duration: int=60) -> MagicMock:
    config = MagicMock()
    config.expiration_days = expiration_days
    config.max_warnings = max_warnings
    config.ban_threshold = ban_threshold
    config.kick_threshold = kick_threshold
    config.timeout_threshold = timeout_threshold
    config.timeout_duration = timeout_duration
    return config