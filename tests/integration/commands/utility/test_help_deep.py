from __future__ import annotations
from locale_keys import locale
from locale_keys.types import LocalizedString
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from discord import app_commands
from tests.helpers.discord import make_command_info
pytestmark = pytest.mark.asyncio

class _HelpViewBase:

    def __init__(self, *args, timeout=3600, **kwargs) -> None:
        self.children: list = []
        self.timeout = timeout

    def add_item(self, item) -> None:
        self.children.append(item)

class _HelpSelectBase:
    options = []
    cash: set = set()

    def __init__(self, client=None, options=None, **kwargs) -> None:
        self.client = client
        self.values: list = []
        self.options = options or kwargs.get('options') or []

@pytest.fixture(autouse=True)
def help_ui_types():
    import discord
    old_view, old_select, old_button, old_embed, old_option = (discord.ui.View, discord.ui.Select, getattr(discord.ui, 'button', None), discord.Embed, discord.SelectOption)
    discord.ui.View = _HelpViewBase
    discord.ui.Select = _HelpSelectBase
    discord.ui.button = lambda **kwargs: lambda fn: fn
    discord.Embed = MagicMock(side_effect=lambda **kw: MagicMock(**kw))
    discord.SelectOption = MagicMock(side_effect=lambda **kw: MagicMock(**kw))
    from commands.utility.help import help as help_command
    yield help_command
    discord.ui.View = old_view
    discord.ui.Select = old_select
    if old_button is not None:
        discord.ui.button = old_button
    discord.Embed = old_embed
    discord.SelectOption = old_option

def _param(name: str, desc: str):
    p = MagicMock()
    p.name = name
    p.description = desc
    return p

def _cmd(name: str, desc: str, *, parameters=None, commands=None, is_group=False):
    c = MagicMock()
    c.name = name
    c.description = desc
    c.parameters = parameters or []
    c.commands = commands or []
    if is_group:
        c.__class__ = app_commands.Group
    return c

def _group(name: str, desc: str, commands):
    g = MagicMock()
    g.name = name
    g.description = desc
    g.commands = commands
    g.__class__ = app_commands.Group
    return g

async def test_help_select_callback_paginates(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    parent = MagicMock()
    parent.qualified_name = 'games'
    parent.name = 'games'
    parent.description = 'games_desc'
    sub_group = _group('sub', 'sub_desc', [_cmd('leaf', 'leaf_desc', parameters=[_param('p1', 'd1')])])
    sub_group.__class__ = app_commands.Group
    top = _group('games', 'games_desc', [sub_group, _cmd('solo', 'solo_desc', parameters=[_param('x', 'y')])])
    info.client.tree = MagicMock()
    info.client.tree.walk_commands = MagicMock(return_value=[top])
    ctx = MagicMock()
    await help_command(info, ctx)
    view = info.reply.await_args.kwargs['view']
    select = view.children[0]
    select.client = info.client
    select.values = ['games']
    interaction = MagicMock()
    interaction.locale = info.locale
    interaction.client = info.client
    interaction.client.tree.walk_commands = MagicMock(return_value=[top])
    interaction.response = MagicMock()
    interaction.response.edit_message = AsyncMock()
    chunks = [_cmd(f'c{i}', 'x' * 500, parameters=[_param(f'p{i}', f'd{i}')]) for i in range(6)]
    bulky = _group('games', 'games_desc', chunks)
    interaction.client.tree.walk_commands = MagicMock(return_value=[bulky])
    select.values = ['games']
    await select.callback(interaction)
    interaction.response.edit_message.assert_awaited_once()
    paginated_view = interaction.response.edit_message.await_args.kwargs.get('view')
    assert paginated_view is not None
    assert len(paginated_view.embeds) > 1
    if hasattr(paginated_view, 'next_button'):
        await paginated_view.next_button(interaction, MagicMock())
    if hasattr(paginated_view, 'previous_button'):
        await paginated_view.previous_button(interaction, MagicMock())

async def test_help_select_get_locale_cache(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    info.client.tree = MagicMock(walk_commands=MagicMock(return_value=[]))
    await help_command(info, MagicMock())
    view = info.reply.await_args.kwargs['view']
    select_cls = type(view.children[0])
    select_cls.cash.clear()
    cached_key = 'commands.help.cached.key'
    select_cls.cash.add(cached_key)
    assert select_cls.get_locale(cached_key, info.locale) == cached_key
    out1 = select_cls.get_locale('commands.help.select.placeholder', info.locale)
    out2 = select_cls.get_locale('commands.help.select.placeholder', info.locale)
    assert out1 == out2

async def test_help_nested_subcommand_group(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    leaf = _cmd('leaf', 'leaf_desc', parameters=[_param('p1', 'd1'), _param('bad', 'bad')])
    inner = _group('inner', 'inner_desc', [leaf])
    top = _group('games', 'games_desc', [inner])
    info.client.tree = MagicMock(walk_commands=MagicMock(return_value=[top]))
    await help_command(info, MagicMock())
    select = info.reply.await_args.kwargs['view'].children[0]
    select.client = info.client
    select.values = ['games']
    interaction = MagicMock()
    interaction.locale = info.locale
    interaction.client = info.client
    interaction.client.tree.walk_commands = MagicMock(return_value=[top])
    interaction.response = MagicMock()
    interaction.response.edit_message = AsyncMock()

    def _flaky_locale(key, locale, **kwargs):
        if key in ('bad', 'd1'):
            raise ValueError('x')
        return LocalizedString(key)(locale, **kwargs)
    with patch.object(type(select), 'get_locale', side_effect=_flaky_locale):
        await select.callback(interaction)
    interaction.response.edit_message.assert_awaited_once()

async def test_help_flat_command_parameters(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    solo = _cmd('solo', 'solo_desc', parameters=[_param('pa', 'da')])
    top = _group('util', 'util_desc', [solo])
    info.client.tree = MagicMock(walk_commands=MagicMock(return_value=[top]))
    await help_command(info, MagicMock())
    select = info.reply.await_args.kwargs['view'].children[0]
    select.client = info.client
    select.values = ['util']
    interaction = MagicMock()
    interaction.locale = info.locale
    interaction.client = info.client
    interaction.client.tree.walk_commands = MagicMock(return_value=[top])
    interaction.response = MagicMock()
    interaction.response.edit_message = AsyncMock()
    await select.callback(interaction)
    interaction.response.edit_message.assert_awaited_once()

async def test_help_no_commands_option(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    info.client.tree = MagicMock(walk_commands=MagicMock(return_value=[]))
    await help_command(info, MagicMock())
    view = info.reply.await_args.kwargs['view']
    select_cls = type(view.children[0])
    opts = select_cls.generate_options(info.client)
    assert len(opts) >= 1

async def test_paginated_help_view_buttons(help_ui_types):
    help_command = help_ui_types
    info = make_command_info()
    parent = MagicMock()
    parent.qualified_name = 'util'
    parent.name = 'util'
    parent.description = 'util_desc'
    info.client.tree = MagicMock()
    info.client.tree.walk_commands = MagicMock(return_value=[MagicMock(parent=parent, name='util', description='d')])
    await help_command(info, MagicMock())
    view = info.reply.await_args.kwargs['view']
    select_cls = type(view.children[0])
    interaction = MagicMock()
    interaction.locale = info.locale
    interaction.client = info.client
    grp = _group('util', 'util_desc', [_cmd('c', 'c_desc')])
    interaction.client.tree.walk_commands = MagicMock(return_value=[grp])
    interaction.response = MagicMock()
    interaction.response.edit_message = AsyncMock()
    select = select_cls(info.client, select_cls.generate_options(info.client))
    select.client = info.client
    select.values = ['util']

    def _raise_on_desc(key, locale, **kwargs):
        if key == 'util_desc':
            raise ValueError('bad')
        return LocalizedString(key)(locale, **kwargs)
    with patch.object(select_cls, 'get_locale', side_effect=_raise_on_desc):
        await select.callback(interaction)
    interaction.response.edit_message.assert_awaited_once()
