from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.setup_wizards as sw_mod
from models import LogEnableModel
from tests.helpers.discord import (
    make_app_command_channel,
    make_guild,
    make_interaction,
    make_member,
    make_permissions,
    make_text_channel,
)

pytestmark = pytest.mark.asyncio

GUILD_ID = "123456789012345678"
TOTAL_PAGES = 4


def _identity_ui(**kwargs):
    def decorator(func):
        return func

    return decorator


@pytest.fixture(scope="module")
def sw():
    with patch("discord.ui.select", _identity_ui), patch("discord.ui.button", _identity_ui):
        importlib.reload(sw_mod)
        yield sw_mod
        importlib.reload(sw_mod)


def _log_enable(**flags: bool) -> LogEnableModel:
    defaults = {k: True for k in LogEnableModel._OPTION_KEYS}
    defaults.update(flags)
    return LogEnableModel(guild_id=GUILD_ID, **defaults)


def _admin_interaction(*, guild: MagicMock | None = None) -> MagicMock:
    guild = guild or make_guild()
    channel = make_text_channel(guild=guild)
    user = make_member(guild_permissions=make_permissions(administrator=True))
    ix = make_interaction(user=user, guild=guild, channel=channel)
    ix.client = MagicMock()
    ix.client.user = MagicMock(id=999999999)
    ix.response.edit_message = AsyncMock()
    ix.response.send_message = AsyncMock()
    channel.permissions_for = MagicMock(
        side_effect=lambda _m: make_permissions(administrator=True, send_messages=True, view_channel=True)
    )
    guild.get_member = MagicMock(return_value=user)
    return ix


def _resolved_app_command_channel(guild: MagicMock) -> MagicMock:
    resolved = make_text_channel(guild=guild)
    resolved.permissions_for = MagicMock(
        return_value=make_permissions(send_messages=True, view_channel=True)
    )
    return make_app_command_channel(guild=guild, resolved=resolved)


@pytest.fixture
def log_api_mocks():
    with (
        patch.object(sw_mod, "api_set_log_channel", new=AsyncMock()) as set_log,
        patch.object(sw_mod, "api_set_log_enable", new=AsyncMock()) as set_enable,
        patch.object(sw_mod, "api_get_log_enable", new=AsyncMock(return_value=_log_enable())) as get_enable,
    ):
        yield {"set_log": set_log, "set_enable": set_enable, "get_enable": get_enable}


class TestLogEventConfigViewRender:
    async def test_render_embed_page_0(self, sw, log_api_mocks) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        embed = await view._render_embed()
        desc = embed.description or ""
        for key in sw.LOG_OPTIONS[:7]:
            assert key in desc
        assert "Page 1/4" in desc

    async def test_render_embed_page_last(self, sw, log_api_mocks) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        view._current_page = TOTAL_PAGES - 1
        embed = await view._render_embed()
        desc = embed.description or ""
        assert sw.LOG_OPTIONS[-1] in desc
        assert f"Page {TOTAL_PAGES}/{TOTAL_PAGES}" in desc

    @pytest.mark.parametrize(
        ("page", "expected_first"),
        [
            (0, "automodRuleCreate"),
            (1, "guildUpdate"),
            (3, "guildRoleCreate"),
        ],
    )
    async def test_page_keys_boundaries(self, sw, page: int, expected_first: str) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        view._current_page = page
        keys = view._page_keys()
        assert keys[0] == expected_first
        assert len(keys) <= view._items_per_page

    async def test_render_embed_icons_match_api(self, sw) -> None:
        guild = make_guild()
        model = _log_enable(automod_rule_create=False, automod_rule_update=True)
        with patch.object(sw_mod, "api_get_log_enable", new=AsyncMock(return_value=model)):
            view = sw.LogEventConfigView("en-US", guild)
            embed = await view._render_embed()
        desc = embed.description or ""
        assert "❌ automodRuleCreate" in desc
        assert "✅ automodRuleUpdate" in desc

    async def test_load_fetches_once(self, sw, log_api_mocks) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        await view._render_embed()
        await view._render_embed()
        log_api_mocks["get_enable"].assert_awaited_once()

    async def test_render_for_message_prefix(self, sw, log_api_mocks) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        embed = await view.render_for_message(prefix="Channel set.")
        assert embed.description is not None
        assert embed.description.startswith("Channel set.")
        assert "Page 1/4" in embed.description


class TestLogEventConfigViewButtons:
    async def test_enable_page_only_current_page(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        view = sw.LogEventConfigView("en-US", guild)
        view._log_enabled = _log_enable(automod_rule_create=False, automod_rule_update=False)
        ix = _admin_interaction(guild=guild)
        await view.enable_page(ix, MagicMock())
        calls = log_api_mocks["set_enable"].await_args_list
        enabled_keys = {list(c.kwargs.keys())[0] for c in calls if c.kwargs}
        assert enabled_keys <= set(view._page_keys())

    async def test_disable_page_only_current_page(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        view = sw.LogEventConfigView("en-US", guild)
        view._log_enabled = _log_enable()
        ix = _admin_interaction(guild=guild)
        await view.disable_page(ix, MagicMock())
        calls = log_api_mocks["set_enable"].await_args_list
        disabled_keys = {list(c.kwargs.keys())[0] for c in calls if c.kwargs}
        assert disabled_keys <= set(view._page_keys())

    async def test_prev_page_clamps_at_zero(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        view = sw.LogEventConfigView("en-US", guild)
        view._log_enabled = _log_enable()
        ix = _admin_interaction(guild=guild)
        await view.prev_page(ix, MagicMock())
        assert view._current_page == 0
        embed = ix.response.edit_message.await_args.kwargs["embed"]
        assert "Page 1/4" in (embed.description or "")

    async def test_next_page_clamps_at_last(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        view = sw.LogEventConfigView("en-US", guild)
        view._log_enabled = _log_enable()
        view._current_page = TOTAL_PAGES - 1
        ix = _admin_interaction(guild=guild)
        await view.next_page(ix, MagicMock())
        assert view._current_page == TOTAL_PAGES - 1
        embed = ix.response.edit_message.await_args.kwargs["embed"]
        assert f"Page {TOTAL_PAGES}/{TOTAL_PAGES}" in (embed.description or "")


class TestLogChannelSelectTransition:
    async def test_channel_select_transition_embed(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        selected = _resolved_app_command_channel(guild)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        kwargs = ix.response.edit_message.await_args.kwargs
        assert isinstance(kwargs["view"], sw.LogEventConfigView)
        desc = kwargs["embed"].description or ""
        assert "automodRuleCreate" in desc
        assert "Page 1/4" in desc
        assert "Log channel set to" in desc

    async def test_channel_select_passes_resolved_channel(self, sw, log_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        selected = _resolved_app_command_channel(guild)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        log_api_mocks["set_log"].assert_awaited_once()
