from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.helpers.view_state import embed_from_edit
from tests.helpers.wizard_flow import admin_interaction, setup_wizards_module

pytestmark = pytest.mark.asyncio


class TestBoosterSetupWizardFlow:
    async def test_booster_initial_ui_lists_steps(self, setup_wizards_module) -> None:
        sw = setup_wizards_module
        view = sw.BoosterSetupView("en-US", MagicMock())
        ix = admin_interaction()
        svc = MagicMock()
        svc.get = AsyncMock(return_value=None)
        import extensions.setup_wizards as sw_mod

        with patch.object(sw_mod, "BoosterService", return_value=svc):
            await view._update_booster_ui(ix)
        embed = embed_from_edit(ix)
        desc = embed.description or ""
        assert "booster category" in desc.lower() or "category" in desc.lower()
        assert "booster role" in desc.lower() or "role" in desc.lower()

    async def test_booster_finish_disables_buttons(self, setup_wizards_module) -> None:
        sw = setup_wizards_module
        view = sw.BoosterSetupView("en-US", MagicMock())
        view.children = [MagicMock(disabled=False) for _ in range(3)]
        ix = admin_interaction()
        await view.finish(ix, MagicMock())
        assert all(item.disabled for item in view.children)
