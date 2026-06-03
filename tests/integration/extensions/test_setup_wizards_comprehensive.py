from __future__ import annotations

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import extensions.setup_wizards as sw_mod
from models import LogEnableModel
from tests.helpers.discord import (
    MockVoiceChannel,
    make_app_command_channel,
    make_guild,
    make_interaction,
    make_member,
    make_permissions,
    make_text_channel,
)
import discord
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.setup_wizards"
GUILD_ID = "123456789012345678"


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


def make_voice_channel() -> MockVoiceChannel:
    ch = MockVoiceChannel()
    ch.id = 777777777
    return ch


def _admin_interaction(*, guild: MagicMock | None = None) -> MagicMock:
    guild = guild or make_guild()
    channel = make_text_channel(guild=guild)
    user = make_member(guild_permissions=make_permissions(administrator=True))
    ix = make_interaction(user=user, guild=guild, channel=channel)
    ix.client = MagicMock()
    ix.client.user = MagicMock(id=999999999)
    ix.response.edit_message = AsyncMock()
    ix.response.send_message = AsyncMock()
    ix.response.send_modal = AsyncMock()
    channel.permissions_for = MagicMock(
        side_effect=lambda _m: make_permissions(administrator=True, send_messages=True, view_channel=True)
    )
    guild.get_member = MagicMock(return_value=user)
    return ix


def _resolved_app_command_channel(
    guild: MagicMock,
    *,
    send_messages: bool = True,
    view_channel: bool = True,
) -> MagicMock:
    resolved = make_text_channel(guild=guild)
    resolved.permissions_for = MagicMock(
        return_value=make_permissions(send_messages=send_messages, view_channel=view_channel)
    )
    return make_app_command_channel(guild=guild, resolved=resolved)


def _non_admin_interaction() -> MagicMock:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    user = make_member(guild_permissions=make_permissions(administrator=False))
    ix = make_interaction(user=user, guild=guild, channel=channel)
    channel.permissions_for = MagicMock(return_value=make_permissions(administrator=False))
    ix.response.send_message = AsyncMock()
    return ix


@pytest.fixture
def wizard_api_mocks():
    with (
        patch.object(sw_mod, "api_set_log_channel", new=AsyncMock()) as set_log,
        patch.object(sw_mod, "api_set_log_enable", new=AsyncMock()) as set_enable,
        patch.object(sw_mod, "api_get_log_enable", new=AsyncMock(return_value=_log_enable())),
        patch.object(sw_mod, "api_get_log_channel", new=AsyncMock(return_value=None)),
        patch.object(sw_mod, "api_set_level_system_status", new=AsyncMock()) as set_level,
        patch.object(sw_mod, "api_set_levelup_channel", new=AsyncMock()),
        patch.object(sw_mod, "api_set_text_cooldown", new=AsyncMock()),
        patch.object(sw_mod, "api_set_voice_cooldown", new=AsyncMock()),
        patch.object(sw_mod, "api_set_xp_scaling", new=AsyncMock()),
        patch.object(sw_mod, "api_get_level_system_status", new=AsyncMock(return_value=False)),
    ):
        yield {"set_log": set_log, "set_enable": set_enable, "set_level": set_level}


class TestHelpers:
    def test_require_admin_true(self, sw) -> None:
        assert sw._require_admin(_admin_interaction()) is True

    def test_require_admin_false_no_guild(self, sw) -> None:
        ix = make_interaction()
        ix.guild = None
        assert sw._require_admin(ix) is False

    async def test_not_admin_reply(self, sw) -> None:
        ix = _non_admin_interaction()
        await sw._not_admin_reply(ix)
        ix.response.send_message.assert_awaited_once()

    def test_loc_or_en(self, sw) -> None:
        assert sw._loc_or_en(make_interaction(locale="de-DE")) == "de-DE"

    def test_loc_or_en_none(self, sw) -> None:
        ix = make_interaction()
        ix.locale = None
        assert sw._loc_or_en(ix) == "en_US"


class TestLogChannelSelectView:
    async def test_channel_select_success(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        selected = _resolved_app_command_channel(guild)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        wizard_api_mocks["set_log"].assert_awaited_once()
        ix.response.edit_message.assert_awaited_once()

    async def test_channel_select_no_permission(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        selected = _resolved_app_command_channel(guild, send_messages=False)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        ix.response.send_message.assert_awaited_once()

    async def test_channel_select_unresolvable(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        view = sw.LogChannelSelectView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        selected = make_app_command_channel(guild=guild, resolved=None, fetch_raises=discord.NotFound)
        await view.on_channel_select(ix, MagicMock(values=[selected]))
        ix.response.send_message.assert_awaited_once()
        wizard_api_mocks["set_log"].assert_not_awaited()

    async def test_channel_select_not_admin(self, sw, wizard_api_mocks) -> None:
        view = sw.LogChannelSelectView("en-US", make_guild())
        ix = _non_admin_interaction()
        await view.on_channel_select(ix, MagicMock(values=[make_text_channel()]))
        ix.response.send_message.assert_awaited_once()

    async def test_channel_select_empty_values(self, sw, wizard_api_mocks) -> None:
        view = sw.LogChannelSelectView("en-US", make_guild())
        await view.on_channel_select(_admin_interaction(), MagicMock(values=[]))


class TestLogEventConfigView:
    async def test_enable_disable_page_and_nav(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        view = sw.LogEventConfigView("en-US", guild)
        view._log_enabled = _log_enable(automod_rule_create=False)
        ix = _admin_interaction(guild=guild)
        button = MagicMock()
        await view.enable_page(ix, button)
        await view.disable_page(ix, button)
        view._current_page = 1
        await view.prev_page(ix, button)
        await view.next_page(ix, button)
        await view.finish(ix, button)

    async def test_not_admin_buttons(self, sw, wizard_api_mocks) -> None:
        view = sw.LogEventConfigView("en-US", make_guild())
        ix = _non_admin_interaction()
        button = MagicMock()
        for name in ("enable_page", "disable_page", "prev_page", "next_page", "finish"):
            await getattr(view, name)(ix, button)


class TestLevelSetupFlow:
    @pytest.mark.parametrize("method", ["easy", "medium", "hard", "very_hard", "extreme"])
    async def test_scaling_buttons(self, sw, wizard_api_mocks, method: str) -> None:
        view = sw.LevelSetupView("en-US", make_guild())
        await getattr(view, method)(_admin_interaction(), MagicMock())

    async def test_cooldown_buttons(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        parent = sw.LevelSetupView("en-US", guild)
        view = sw.LevelCooldownView("en-US", guild, parent)
        ix = _admin_interaction(guild=guild)
        for name in ("fast", "normal", "slow"):
            await getattr(view, name)(ix, MagicMock())

    async def test_channel_select_and_skip(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        guild.get_member = MagicMock(return_value=make_member())
        parent = sw.LevelSetupView("en-US", guild)
        view = sw.LevelChannelView("en-US", guild, parent)
        selected = _resolved_app_command_channel(guild)
        await view.on_channel_select(_admin_interaction(guild=guild), MagicMock(values=[selected]))
        assert parent.completed is True
        parent2 = sw.LevelSetupView("en-US", guild)
        view2 = sw.LevelChannelView("en-US", guild, parent2)
        await view2.skip(_admin_interaction(guild=guild), MagicMock())
        assert parent2.completed is True

    async def test_channel_error_paths(self, sw, wizard_api_mocks) -> None:
        guild = make_guild()
        parent = sw.LevelSetupView("en-US", guild)
        view = sw.LevelChannelView("en-US", guild, parent)
        guild.get_member = MagicMock(return_value=None)
        await view.on_channel_select(
            _admin_interaction(guild=guild),
            MagicMock(values=[_resolved_app_command_channel(guild)]),
        )
        guild.get_member = MagicMock(return_value=make_member())
        selected = _resolved_app_command_channel(guild, send_messages=False, view_channel=False)
        await view.on_channel_select(_admin_interaction(guild=guild), MagicMock(values=[selected]))


class TestBoosterSetup:
    async def test_refresh_finish_and_modals(self, sw) -> None:
        guild = make_guild()
        view = sw.BoosterSetupView("en-US", guild)
        ix = _admin_interaction(guild=guild)
        svc = MagicMock()
        svc.get = AsyncMock(return_value="111")
        with patch.object(sw_mod, "BoosterService", return_value=svc):
            await view._refresh(ix)
            await view.finish(ix, MagicMock())
            await view.set_channel(ix, MagicMock())
            await view.set_role(ix, MagicMock())

    async def test_booster_channel_modal_paths(self, sw) -> None:
        guild = make_guild()
        parent = sw.BoosterSetupView("en-US", guild)
        modal = sw.BoosterChannelModal("en-US", guild, parent)
        ix = _admin_interaction(guild=guild)
        modal.children = [MagicMock(value="bad")]
        await modal.on_submit(ix)
        modal.children = [MagicMock(value="999")]
        guild.get_channel = MagicMock(return_value=None)
        await modal.on_submit(ix)
        vc = make_voice_channel()
        guild.get_channel = MagicMock(return_value=vc)
        modal.children = [MagicMock(value="777777777")]
        svc = MagicMock()
        svc.add = AsyncMock()
        with (
            patch.object(sw_mod, "BoosterService", return_value=svc),
            patch.object(sw_mod.discord, "VoiceChannel", MockVoiceChannel),
        ):
            await modal.on_submit(ix)

    async def test_booster_role_modal_paths(self, sw) -> None:
        guild = make_guild()
        parent = sw.BoosterSetupView("en-US", guild)
        modal = sw.BoosterRoleModal("en-US", guild, parent)
        ix = _admin_interaction(guild=guild)
        modal.children = [MagicMock(value="bad")]
        await modal.on_submit(ix)
        modal.children = [MagicMock(value="555555555")]
        guild.get_role = MagicMock(return_value=None)
        await modal.on_submit(ix)
        role = MagicMock()
        role.mention = "<@&555>"
        guild.get_role = MagicMock(return_value=role)
        svc = MagicMock()
        svc.add = AsyncMock()
        with patch.object(sw_mod, "BoosterService", return_value=svc):
            await modal.on_submit(ix)


class TestSetupWizardCommands:
    async def test_logs_already_configured(self, sw, wizard_api_mocks) -> None:
        with patch.object(sw_mod, "api_get_log_channel", new=AsyncMock(return_value="444444444")):
            group = sw.SetupWizardCommands(MagicMock())
            ix = _admin_interaction()
            await group.logs(ix)
            ix.response.send_message.assert_awaited_once()

    async def test_logs_starts_wizard(self, sw, wizard_api_mocks) -> None:
        group = sw.SetupWizardCommands(MagicMock())
        await group.logs(_admin_interaction())

    async def test_level_already_active(self, sw, wizard_api_mocks) -> None:
        with patch.object(sw_mod, "api_get_level_system_status", new=AsyncMock(return_value=True)):
            group = sw.SetupWizardCommands(MagicMock())
            await group.level(_admin_interaction())

    async def test_level_wizard_completes(self, sw, wizard_api_mocks) -> None:
        group = sw.SetupWizardCommands(MagicMock())

        async def _fake_wait(self):
            self.completed = True

        with patch.object(sw.LevelSetupView, "wait", _fake_wait):
            await group.level(_admin_interaction())
        wizard_api_mocks["set_level"].assert_awaited()

    async def test_giveaway_and_booster(self, sw, wizard_api_mocks) -> None:
        group = sw.SetupWizardCommands(MagicMock())
        with patch("commands.giveaway.start.start_giveaway", new=AsyncMock()):
            await group.giveaway(_admin_interaction())
        await group.booster(_admin_interaction())

    async def test_not_admin_commands(self, sw, wizard_api_mocks) -> None:
        group = sw.SetupWizardCommands(MagicMock())
        ix = _non_admin_interaction()
        for cmd in (group.logs, group.level, group.giveaway, group.booster):
            await cmd(ix)


async def test_cog_unload() -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    await bot.cogs["SetupWizardsCog"].cog_unload()
    bot.tree.remove_command.assert_called_once()
