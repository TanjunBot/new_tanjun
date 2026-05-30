from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.start import CustomNameModal, SponsorView
from tests.integration.commands.admin.conftest import make_view_interaction
from tests.integration.commands.giveaway.test_giveaway_start_deep import _builder


pytestmark = pytest.mark.asyncio


async def test_custom_name_modal_on_timeout(admin_command_info):
    view = _builder(admin_command_info)
    modal = CustomNameModal(view, admin_command_info, "t", "d")
    await modal.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_sponsor_view_unauthorized(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    interaction = make_view_interaction(user=MagicMock(id=999))
    ok = await sponsor_view.interaction_check(interaction)
    assert ok is False


async def test_sponsor_view_timeout(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    await sponsor_view.on_timeout()
    view.generator_message.edit.assert_awaited()


async def test_sponsor_view_confirm_empty_selection(admin_command_info):
    view = _builder(admin_command_info)
    sponsor_view = SponsorView(admin_command_info, view)
    sponsor_view.selected_user = []
    interaction = make_view_interaction(user=admin_command_info.user)
    interaction.data = {"custom_id": "confirm"}
    interaction.response.edit_message = AsyncMock()
    await sponsor_view.on_button_press(interaction)
    assert view.giveaway_data["sponsor"] is None
