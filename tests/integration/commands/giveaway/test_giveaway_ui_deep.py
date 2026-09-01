from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.giveaway.start import GiveawayBuilder
from tests.helpers.view_state import view_from_reply
from tests.integration.commands.admin.conftest import make_view_interaction

pytestmark = pytest.mark.asyncio


async def test_giveaway_builder_initial_state(admin_command_info) -> None:
    channel = admin_command_info.channel
    builder = GiveawayBuilder(admin_command_info, "Prize Title", channel)
    assert builder.giveaway_data["title"] == "Prize Title"
    assert builder.giveaway_data["winners"] == 1
    assert len(builder.children) >= 10


async def test_giveaway_builder_update_embed_fields(admin_command_info) -> None:
    channel = admin_command_info.channel
    builder = GiveawayBuilder(admin_command_info, "Test Giveaway", channel)
    builder.generator_message = MagicMock(edit=AsyncMock())
    await builder.update_embed()
    builder.generator_message.edit.assert_awaited_once()
    kwargs = builder.generator_message.edit.await_args.kwargs
    embed = kwargs["embed"]
    assert embed.title == "Test Giveaway"
    assert len(embed.fields) >= 5


async def test_giveaway_builder_wrong_user(admin_command_info) -> None:
    builder = GiveawayBuilder(admin_command_info, "T", admin_command_info.channel)
    wrong = make_view_interaction(MagicMock())
    wrong.user.id = 999999999
    result = await builder.interaction_check(wrong)
    assert result is False


async def test_giveaway_builder_has_confirm_button(admin_command_info) -> None:
    builder = GiveawayBuilder(admin_command_info, "T", admin_command_info.channel)
    custom_ids = [getattr(c, "custom_id", None) for c in builder.children]
    assert "confirm" in custom_ids
    assert "preview" in custom_ids
