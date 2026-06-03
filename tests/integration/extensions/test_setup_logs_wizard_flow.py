from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.view_state import (
    assert_embed_contains_keys,
    assert_embed_page,
    edit_description,
    embed_from_edit,
)
from tests.helpers.wizard_flow import (
    admin_interaction,
    log_enable_model,
    non_admin_interaction,
    resolved_app_command_channel,
    setup_wizards_module,
    wizard_api_mocks,
)

pytestmark = pytest.mark.asyncio

LOG_OPTIONS = [
    "automodRuleCreate",
    "automodRuleUpdate",
    "automodRuleDelete",
    "automodAction",
    "guild_channelDelete",
    "guild_channelCreate",
    "guild_channelUpdate",
]
PAGE_ONE_KEYS = LOG_OPTIONS[:7]
ITEMS_PER_PAGE = 7
TOTAL_PAGES = 4


class TestLogChannelSelectTransition:
    async def test_channel_select_renders_page_one(
        self, setup_wizards_module, wizard_api_mocks
    ) -> None:
        sw = setup_wizards_module
        guild = MagicMock()
        guild.id = 123456789012345678
        guild.get_member = MagicMock(return_value=MagicMock())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = admin_interaction(guild=guild)
        selected = resolved_app_command_channel(guild)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        wizard_api_mocks["set_log"].assert_awaited_once()
        embed = embed_from_edit(ix)
        desc = edit_description(ix)
        assert_embed_page(embed, 1, TOTAL_PAGES)
        assert_embed_contains_keys(embed, PAGE_ONE_KEYS)
        assert "Log channel set to" in desc

    async def test_channel_select_non_admin(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LogChannelSelectView("en-US", MagicMock())
        ix = non_admin_interaction()
        await view.on_channel_select(ix, MagicMock(values=[MagicMock()]))
        ix.response.send_message.assert_awaited_once()
        wizard_api_mocks["set_log"].assert_not_awaited()


class TestLogEventConfigView:
    async def test_page_one_keys(self, setup_wizards_module) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        assert view._page_keys() == PAGE_ONE_KEYS

    async def test_prev_page_at_zero_unchanged(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        view._log_enabled = log_enable_model()
        ix = admin_interaction()
        await view.prev_page(ix, MagicMock())
        embed = embed_from_edit(ix)
        assert_embed_page(embed, 1, TOTAL_PAGES)

    async def test_next_page_to_two_and_back(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        view._log_enabled = log_enable_model()
        ix = admin_interaction()
        await view.next_page(ix, MagicMock())
        embed = embed_from_edit(ix, call_index=-1)
        assert_embed_page(embed, 2, TOTAL_PAGES)
        await view.prev_page(ix, MagicMock())
        embed = embed_from_edit(ix, call_index=-1)
        assert_embed_page(embed, 1, TOTAL_PAGES)

    async def test_enable_page_only_toggles_current_page(
        self, setup_wizards_module, wizard_api_mocks
    ) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        view._log_enabled = log_enable_model()
        for key in PAGE_ONE_KEYS:
            idx = sw.LOG_OPTIONS.index(key)
            view._log_enabled.set_option(idx, False)
        ix = admin_interaction()
        await view.enable_page(ix, MagicMock())
        set_enable = wizard_api_mocks["set_enable"]
        assert set_enable.await_count == len(PAGE_ONE_KEYS)
        for call in set_enable.await_args_list:
            kwargs = call.kwargs
            enabled_keys = [k for k, v in kwargs.items() if k in PAGE_ONE_KEYS and v is True]
            assert len(enabled_keys) == 1

    async def test_finish_disables_children(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        view._log_enabled = log_enable_model()
        view.children = [MagicMock(disabled=False) for _ in range(5)]
        ix = admin_interaction()
        await view.finish(ix, MagicMock())
        assert all(item.disabled for item in view.children)
        embed = embed_from_edit(ix)
        assert "Log Setup Complete" in (embed.title or "")

    async def test_render_embed_first_page(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LogEventConfigView("en-US", MagicMock())
        embed = await view._render_embed()
        assert_embed_page(embed, 1, TOTAL_PAGES)
        assert_embed_contains_keys(embed, PAGE_ONE_KEYS)


class TestSetupLogsCommand:
    async def test_logs_starts_wizard(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        group = sw.SetupWizardCommands(MagicMock())
        ix = admin_interaction()
        await group.logs(ix)
        ix.response.send_message.assert_awaited_once()
        kwargs = ix.response.send_message.await_args.kwargs
        assert kwargs.get("view") is not None
        assert "Log Setup Wizard" in (kwargs["embed"].title or "")

    async def test_logs_already_configured(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        import extensions.setup_wizards as sw_mod

        with patch.object(sw_mod, "api_get_log_channel", new=AsyncMock(return_value="444444444")):
            group = sw.SetupWizardCommands(MagicMock())
            ix = admin_interaction()
            await group.logs(ix)
            ix.response.send_message.assert_awaited_once()
            embed = ix.response.send_message.await_args.kwargs["embed"]
            assert "Already Configured" in (embed.title or "")
