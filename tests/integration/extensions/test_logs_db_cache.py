"""Verify log event handlers share cached get_log_enable DB access."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from api import _LOG_ENABLE_SELECT, clear_db_read_caches
from tests.helpers.discord import make_guild, make_member
from tests.helpers.factories import GUILD_ID
from tests.helpers.extensions import async_audit_logs
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.logs"


@pytest.fixture(autouse=True)
def _reset_log_caches() -> None:
    clear_db_read_caches()
    yield
    clear_db_read_caches()


def _count_log_enable_queries(execute: AsyncMock) -> int:
    return sum(
        1
        for call in execute.await_args_list
        if call.args and _LOG_ENABLE_SELECT in call.args[0]
    )


async def test_concurrent_member_updates_one_log_enable_query() -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild(guild_id=int(GUILD_ID))
    guild.audit_logs = MagicMock(return_value=async_audit_logs())

    before = make_member()
    before.guild = guild
    before.display_name = "a"
    before.display_avatar = MagicMock()
    before.display_avatar.read = AsyncMock(return_value=b"")
    before.roles = []

    after = make_member()
    after.guild = guild
    after.display_name = "b"
    after.display_avatar = MagicMock()
    after.display_avatar.read = AsyncMock(return_value=b"")
    after.roles = []

    log_enable_row = (
        GUILD_ID,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        1,
        1,
        1,
    )

    execute = AsyncMock(
        side_effect=lambda q, p=None, bot=None: (
            [log_enable_row]
            if _LOG_ENABLE_SELECT in q
            else ([] if "logRoleBlacklist" in q or "logUserBlacklist" in q else None)
        )
    )

    with (
        patch("api.execute_query", new=execute),
        patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=None)),
        patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=[])),
        patch("extensions.logs.log_event_producer", new=AsyncMock()),
    ):
        await asyncio.gather(*[cog.on_member_update(before, after) for _ in range(30)])

    assert _count_log_enable_queries(execute) == 1


async def test_concurrent_message_deletes_one_log_enable_query() -> None:
    bot = await load_extension_bot(EXTENSION, fire_ready=False)
    cog = bot.cogs["LogsCog"]
    guild = make_guild(guild_id=int(GUILD_ID))
    message = MagicMock()
    message.guild = guild
    message.author = make_member()
    message.channel = MagicMock()
    message.channel.id = 123456789
    message.content = "hello"
    message.attachments = []
    message.embeds = []

    log_enable_row = (
        GUILD_ID,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        1,
        1,
        1,
    )

    execute = AsyncMock(
        side_effect=lambda q, p=None, bot=None: (
            [log_enable_row]
            if _LOG_ENABLE_SELECT in q
            else ([] if "logRoleBlacklist" in q or "logUserBlacklist" in q else None)
        )
    )

    with (
        patch("api.execute_query", new=execute),
        patch("extensions.logs.is_log_entity_blacklisted", new=AsyncMock(return_value=None)),
        patch("extensions.logs.get_log_blacklist", new=AsyncMock(return_value=[])),
        patch("extensions.logs.log_event_producer", new=AsyncMock()),
    ):
        await asyncio.gather(*[cog.on_message_delete(message) for _ in range(30)])

    assert _count_log_enable_queries(execute) == 1


async def test_set_log_enable_invalidates_shared_cache() -> None:
    execute = AsyncMock(
        side_effect=lambda q, p=None, bot=None: (
            [
                (
                    GUILD_ID,
                    1,
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    0,
                    0,
                    1,
                    1,
                    1,
                )
            ]
            if _LOG_ENABLE_SELECT in q
            else None
        )
    )
    from api import get_log_enable, set_log_enable

    with (
        patch("api.execute_query", new=execute),
        patch("api.execute_action", new=AsyncMock()),
    ):
        await asyncio.gather(*[get_log_enable(GUILD_ID) for _ in range(30)])
        assert _count_log_enable_queries(execute) == 1
        await set_log_enable(GUILD_ID, memberJoin=False)
        await asyncio.gather(*[get_log_enable(GUILD_ID) for _ in range(30)])
    assert _count_log_enable_queries(execute) == 2

