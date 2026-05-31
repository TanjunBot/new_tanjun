from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from extensions.administration import AdministrationCog
from tests.helpers.discord import make_guild, make_member, make_message, make_text_channel
from tests.integration.extensions.conftest import load_extension_bot

pytestmark = pytest.mark.asyncio

EXTENSION = "extensions.administration"
COG_NAME = "AdministrationCog"
MOCK_ADMIN_IDS = [42424242, 51515151]
ADMIN_ID = MOCK_ADMIN_IDS[0]
NON_ADMIN_ID = 88888888


def make_context(
    bot: MagicMock,
    *,
    author_id: int,
) -> MagicMock:
    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member(user_id=author_id)
    ctx = MagicMock()
    ctx.author = author
    ctx.guild = guild
    ctx.channel = channel
    ctx.bot = bot
    ctx.send = AsyncMock()
    ctx.message = make_message(author=author, guild=guild, channel=channel)
    return ctx


@pytest.fixture
def mock_admin_ids() -> list[int]:
    return list(MOCK_ADMIN_IDS)


@pytest.fixture
async def cog(mock_admin_ids: list[int]) -> AdministrationCog:
    with patch("extensions.administration.config.adminIds", mock_admin_ids):
        bot = await load_extension_bot(EXTENSION, fire_ready=False)
    return bot.cogs[COG_NAME]


@pytest.fixture
def bot(cog: AdministrationCog) -> MagicMock:
    return cog.bot


@pytest.mark.parametrize(
    "method_name,extra_kwargs",
    [
        ("sync", {}),
        ("feedback", {"content": "hello"}),
        ("me", {}),
    ],
)
async def test_non_admin_denied(
    cog: AdministrationCog,
    bot: MagicMock,
    mock_admin_ids: list[int],
    method_name: str,
    extra_kwargs: dict,
) -> None:
    ctx = make_context(bot, author_id=NON_ADMIN_ID)
    with patch("extensions.administration.config.adminIds", mock_admin_ids):
        await getattr(cog, method_name)(ctx, **extra_kwargs)
    ctx.send.assert_not_called()


@pytest.mark.asyncio
async def test_admin_allowed_sync(
    cog: AdministrationCog,
    bot: MagicMock,
    mock_admin_ids: list[int],
) -> None:
    ctx = make_context(bot, author_id=ADMIN_ID)
    bot.tree = MagicMock()
    bot.tree.sync = AsyncMock(return_value=[MagicMock()])
    with patch("extensions.administration.config.adminIds", mock_admin_ids):
        await cog.sync(ctx)
    ctx.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_allowed_feedback(
    cog: AdministrationCog,
    bot: MagicMock,
    mock_admin_ids: list[int],
) -> None:
    ctx = make_context(bot, author_id=ADMIN_ID)
    with (
        patch("extensions.administration.config.adminIds", mock_admin_ids),
        patch("extensions.administration.addFeedback", new=AsyncMock()),
    ):
        await cog.feedback(ctx, content="hello")
    ctx.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_admin_allowed_me(
    cog: AdministrationCog,
    bot: MagicMock,
    mock_admin_ids: list[int],
) -> None:
    ctx = make_context(bot, author_id=ADMIN_ID)
    with patch("extensions.administration.config.adminIds", mock_admin_ids):
        await cog.me(ctx)
    ctx.send.assert_awaited_once()


async def test_second_configured_admin_allowed(
    cog: AdministrationCog,
    bot: MagicMock,
    mock_admin_ids: list[int],
) -> None:
    ctx = make_context(bot, author_id=MOCK_ADMIN_IDS[1])
    bot.tree = MagicMock()
    bot.tree.sync = AsyncMock(return_value=[MagicMock()])
    with patch("extensions.administration.config.adminIds", mock_admin_ids):
        await cog.sync(ctx)
    ctx.send.assert_awaited_once()
