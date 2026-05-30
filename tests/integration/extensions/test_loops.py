from __future__ import annotations

import importlib

import pytest

from tests.helpers.extension_loader import (
    get_tree_commands,
)
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.loops"
COG_NAME = "LoopCog"


async def test_module_exposes_setup():
    module = importlib.import_module(EXTENSION)
    assert hasattr(module, "setup")
    assert callable(module.setup)


async def test_setup_registers_cog():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert COG_NAME in bot.cogs


async def test_setup_calls_add_cog_once():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    bot.add_cog.assert_awaited_once()


async def test_get_cog_returns_registered_instance():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.get_cog(COG_NAME) is bot.cogs[COG_NAME]


async def test_cog_stores_bot_reference():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert bot.cogs[COG_NAME].bot is bot


async def test_cog_has_loop_pollTwitchStreams():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "pollTwitchStreams")


async def test_cog_has_loop_sendSendReadyGiveaways():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "sendSendReadyGiveaways")


async def test_cog_has_loop_endGiveawaysLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "endGiveawaysLoop")


async def test_cog_has_loop_checkVoiceUsers():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "checkVoiceUsers")


async def test_cog_has_loop_clearNotifiedUsersLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "clearNotifiedUsersLoop")


async def test_cog_has_loop_addVoiceUserLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "addVoiceUserLoop")


async def test_cog_has_loop_refillAiTokenLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "refillAiTokenLoop")


async def test_cog_has_loop_pingServerLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "pingServerLoop")


async def test_cog_has_loop_backupDatabaseLoop():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "backupDatabaseLoop")


async def test_cog_has_loop_removeExpiredClaimedBoosterRoles():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "removeExpiredClaimedBoosterRoles")


async def test_cog_has_loop_removeExpiredClaimedBoosterChannels():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "removeExpiredClaimedBoosterChannels")


async def test_cog_has_loop_sendScheduledMessages():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "sendScheduledMessages")


async def test_cog_has_loop_sendPokemonWerbung():
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    assert hasattr(bot.cogs[COG_NAME], "sendPokemonWerbung")


async def test_on_ready_does_not_add_tree_commands():
    bot = await load_extension_bot(EXTENSION)
    assert get_tree_commands(bot) == []


async def test_on_ready_starts_background_loops():
    bot = await load_extension_bot(EXTENSION)
    cog = bot.cogs[COG_NAME]
    assert cog.pollTwitchStreams.start.called
    assert cog.endGiveawaysLoop.start.called
    assert cog.sendScheduledMessages.start.called
