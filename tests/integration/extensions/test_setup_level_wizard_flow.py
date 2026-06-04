from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.helpers.view_state import edit_description, embed_from_edit
from tests.helpers.wizard_flow import (
    admin_interaction,
    non_admin_interaction,
    resolved_app_command_channel,
    setup_wizards_module,
    wizard_api_mocks,
)

pytestmark = pytest.mark.asyncio


class TestLevelSetupWizardFlow:
    async def test_easy_scaling_shows_cooldown_step(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LevelSetupView("en-US", MagicMock())
        ix = admin_interaction()
        await view.easy(ix, MagicMock())
        desc = edit_description(ix)
        assert "XP difficulty" in desc
        assert "**Step 2:**" in desc
        assert "**Fast**" in desc and "30s text" in desc
        assert "**Normal**" in desc and "120s voice" in desc
        assert "**Slow**" in desc and "300s voice" in desc
        kwargs = ix.response.edit_message.await_args.kwargs
        assert isinstance(kwargs.get("view"), sw.LevelCooldownView)

    async def test_cooldown_normal_shows_channel_step(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        parent = sw.LevelSetupView("en-US", MagicMock())
        view = sw.LevelCooldownView("en-US", MagicMock(), parent)
        ix = admin_interaction()
        await view.normal(ix, MagicMock())
        desc = edit_description(ix)
        assert "60" in desc
        kwargs = ix.response.edit_message.await_args.kwargs
        assert isinstance(kwargs.get("view"), sw.LevelChannelView)

    async def test_channel_select_completes_setup(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        guild = MagicMock()
        guild.id = 123456789012345678
        guild.get_member = MagicMock(return_value=MagicMock())
        parent = sw.LevelSetupView("en-US", guild)
        view = sw.LevelChannelView("en-US", guild, parent)
        ix = admin_interaction(guild=guild)
        selected = resolved_app_command_channel(guild)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        assert parent.completed is True
        embed = embed_from_edit(ix)
        assert "complete" in (embed.title or "").lower() or "Channel Set" in (embed.title or "")

    async def test_channel_skip_completes(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        parent = sw.LevelSetupView("en-US", MagicMock())
        view = sw.LevelChannelView("en-US", MagicMock(), parent)
        ix = admin_interaction()
        await view.skip(ix, MagicMock())
        assert parent.completed is True

    async def test_scaling_not_admin(self, setup_wizards_module, wizard_api_mocks) -> None:
        sw = setup_wizards_module
        view = sw.LevelSetupView("en-US", MagicMock())
        ix = non_admin_interaction()
        await view.medium(ix, MagicMock())
        ix.response.send_message.assert_awaited_once()
