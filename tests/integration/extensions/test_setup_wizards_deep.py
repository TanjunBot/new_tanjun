from __future__ import annotations

import inspect
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from extensions.setup_wizards import (
    BoosterChannelModal,
    BoosterRoleModal,
    BoosterSetupView,
    LevelChannelView,
    LevelCooldownView,
    LevelSetupView,
    LogChannelSelectView,
    LogEventConfigView,
    SetupWizardCommands,
)
from tests.helpers.discord import make_guild, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.setup_wizards"


@pytest.fixture(autouse=True)
def mock_setup_apis():
    with (
        patch("extensions.setup_wizards.api_set_log_channel", new=AsyncMock()),
        patch("extensions.setup_wizards.api_set_log_enable", new=AsyncMock()),
        patch("extensions.setup_wizards.api_get_log_enable", new=AsyncMock(return_value=MagicMock())),
        patch("extensions.setup_wizards.api_get_log_channel", new=AsyncMock(return_value=None)),
        patch("extensions.setup_wizards.api_set_level_system_status", new=AsyncMock()),
        patch("extensions.setup_wizards.api_set_levelup_channel", new=AsyncMock()),
        patch("extensions.setup_wizards.api_set_text_cooldown", new=AsyncMock()),
        patch("extensions.setup_wizards.api_set_voice_cooldown", new=AsyncMock()),
        patch("extensions.setup_wizards.api_set_xp_scaling", new=AsyncMock()),
        patch("extensions.setup_wizards.api_get_level_system_status", new=AsyncMock(return_value=False)),
    ):
        yield


async def test_setup_wizard_commands_invoke():
    bot = MagicMock()
    bot.tree = MagicMock()
    group = SetupWizardCommands(bot)
    interaction = MagicMock()
    interaction.guild = make_guild()
    interaction.user = MagicMock()
    interaction.user.guild_permissions = MagicMock(administrator=True)
    interaction.locale = "en-US"
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    interaction.response.defer = AsyncMock()
    for name in ("logs", "level", "booster"):
        handler = getattr(group, name)
        await handler(interaction)


async def test_log_channel_select_view_callbacks():
    view = LogChannelSelectView("en-US", make_guild())
    view.channel_select = MagicMock()
    view.channel_select.values = [make_text_channel()]
    for name in dir(view):
        attr = getattr(view, name, None)
        if callable(attr) and hasattr(attr, "__discord_ui_model_type__"):
            continue
        if name.startswith("on_") or (callable(attr) and inspect.iscoroutinefunction(attr)):
            interaction = MagicMock()
            interaction.response = MagicMock()
            interaction.response.defer = AsyncMock()
            interaction.followup = MagicMock()
            interaction.followup.send = AsyncMock()
            try:
                await attr(interaction)
            except TypeError:
                pass


async def test_level_setup_views():
    guild = make_guild()
    for view_cls in (LevelSetupView, LevelCooldownView, LevelChannelView, BoosterSetupView, LogEventConfigView):
        if view_cls is LevelCooldownView or view_cls is LevelChannelView:
            parent = LevelSetupView("en-US", guild)
            view = view_cls("en-US", guild, parent)
        else:
            view = view_cls("en-US", guild)
        assert view is not None


async def test_booster_modals_on_submit():
    parent = BoosterSetupView("en-US", make_guild())
    modal = BoosterChannelModal("en-US", make_guild(), parent)
    modal.channel_id = MagicMock(value="444444444")
    modal.role_id = MagicMock(value="555555555")
    interaction = MagicMock()
    interaction.user = MagicMock()
    interaction.user.guild_permissions = MagicMock(administrator=True)
    interaction.guild = make_guild()
    interaction.response = MagicMock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = MagicMock()
    interaction.followup.send = AsyncMock()
    with patch("extensions.setup_wizards.BoosterService") as svc:
        svc.return_value.set = AsyncMock()
        await modal.on_submit(interaction)

    modal2 = BoosterRoleModal("en-US", make_guild(), parent)
    modal2.role_id = MagicMock(value="555555555")
    await modal2.on_submit(interaction)


async def test_setup_wizards_cog_on_ready():
    bot = await load_extension_bot(EXTENSION, fire_ready=True)
    assert bot.tree.add_command.called
