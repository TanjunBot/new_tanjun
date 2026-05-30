"""Integration tests for commands.math.num2word."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.integration.commands.conftest import embed_from_reply, make_role, make_user
from tests.helpers.discord import make_command_info, make_guild, make_member, make_permissions, make_text_channel


from commands.math.num2word import num2word as command_fn


@pytest.mark.asyncio
async def test_num2word_en():
    info = make_command_info()
    await command_fn(info, 42, "en")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_num2word_de():
    info = make_command_info(locale="de")
    await command_fn(info, 100, "de")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_num2word_invalid_locale_falls_back():
    info = make_command_info()
    await command_fn(info, 7, "invalid_locale")
    embed_from_reply(info.reply)


@pytest.mark.asyncio
async def test_num2word_en_us_alias():
    info = make_command_info()
    await command_fn(info, 1, "en_US")
    embed_from_reply(info.reply)
