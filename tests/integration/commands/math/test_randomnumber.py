"""Integration tests for commands.math.randomnumber."""

from __future__ import annotations

import pytest

from commands.math.randomnumber import random_number_command as command_fn
from tests.helpers.discord import make_command_info
from tests.integration.commands.conftest import embed_from_reply


@pytest.mark.asyncio
async def test_random_success():
    info = make_command_info()
    await command_fn(info, 1, 10, 3)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_random_invalid_range():
    info = make_command_info()
    await command_fn(info, 10, 1, 1)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_random_invalid_amount():
    info = make_command_info()
    await command_fn(info, 1, 10, 0)
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_random_rejects_excessive_amount():
    info = make_command_info()
    await command_fn(info, 1, 10, 11)
    embed = embed_from_reply(info.reply)
    assert embed.description and ("at least 1" in embed.description.lower() or "number" in embed.description.lower())


@pytest.mark.asyncio
async def test_random_single_value():
    info = make_command_info()
    await command_fn(info, 5, 5, 1)
    embed_from_reply(info.reply)
