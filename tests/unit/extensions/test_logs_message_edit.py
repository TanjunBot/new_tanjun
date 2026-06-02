from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

import tests.mock_config as mock_config

mock_config.patch_config_module()

from extensions import logs  # noqa: E402

pytestmark = pytest.mark.unit

PREFERRED_LOCALE_GUARD_PATTERN = re.compile(
    r"(?P<true>[^\n#]+?)\s+if\s+hasattr\((?P<obj>[^,]+),\s*[\"']preferred_locale[\"']\)\s+else\s+[\"']en_US[\"']"
)


def _message(*, guild: object, content: str) -> SimpleNamespace:
    return SimpleNamespace(
        guild=guild,
        content=content,
        attachments=[],
        author=SimpleNamespace(id=42, mention="<@42>", roles=[]),
        channel=None,
        jump_url="https://discord.com/channels/1/2/3",
    )


@pytest.mark.asyncio
async def test_on_message_edit_uses_guild_preferred_locale() -> None:
    cog = logs.LogsCog(bot=MagicMock())
    guild = SimpleNamespace(id=123, preferred_locale="de-DE")
    before = _message(guild=guild, content="before")
    after = _message(guild=guild, content="after")

    logs.get_log_enable = AsyncMock(return_value=SimpleNamespace(message_edit=True))  # type: ignore[method-assign]
    logs.is_log_entity_blacklisted = AsyncMock(return_value=False)  # type: ignore[method-assign]
    logs.get_log_blacklist = AsyncMock(return_value=[])  # type: ignore[method-assign]
    logs._is_channel_or_category_blacklisted = AsyncMock(return_value=False)  # type: ignore[method-assign]
    logs.log_event_producer = AsyncMock()  # type: ignore[method-assign]
    logs.tanjunLocalizer.localize = MagicMock(return_value="localized")  # type: ignore[method-assign]

    await cog.on_message_edit(before, after)

    first_call = logs.tanjunLocalizer.localize.call_args_list[0]
    assert first_call.args[0] == "de-DE"


@pytest.mark.asyncio
async def test_on_message_edit_falls_back_to_en_us_without_guild_locale() -> None:
    cog = logs.LogsCog(bot=MagicMock())
    guild = SimpleNamespace(id=123)
    before = _message(guild=guild, content="before")
    after = _message(guild=guild, content="after")

    logs.get_log_enable = AsyncMock(return_value=SimpleNamespace(message_edit=True))  # type: ignore[method-assign]
    logs.is_log_entity_blacklisted = AsyncMock(return_value=False)  # type: ignore[method-assign]
    logs.get_log_blacklist = AsyncMock(return_value=[])  # type: ignore[method-assign]
    logs._is_channel_or_category_blacklisted = AsyncMock(return_value=False)  # type: ignore[method-assign]
    logs.log_event_producer = AsyncMock()  # type: ignore[method-assign]
    logs.tanjunLocalizer.localize = MagicMock(return_value="localized")  # type: ignore[method-assign]

    await cog.on_message_edit(before, after)

    first_call = logs.tanjunLocalizer.localize.call_args_list[0]
    assert first_call.args[0] == "en_US"


class _GuildStub:
    def __init__(self, **kwargs: object) -> None:
        self.__dict__.update(kwargs)

    def __getattr__(self, _name: str) -> object:
        return None


@pytest.mark.asyncio
async def test_on_guild_update_uses_after_guild_and_preferred_locale() -> None:
    cog = logs.LogsCog(bot=MagicMock())
    before = _GuildStub(id=11, preferred_locale="en-US", name="old", emojis=[], features=[])
    after = _GuildStub(id=11, preferred_locale="de-DE", name="new", emojis=[], features=[])

    logs.get_log_enable = AsyncMock(return_value=SimpleNamespace(guild_update=True))  # type: ignore[method-assign]
    logs.log_event_producer = AsyncMock()  # type: ignore[method-assign]
    logs.tanjunLocalizer.localize = MagicMock(return_value="localized")  # type: ignore[method-assign]

    await cog.on_guild_update(before, after)

    logs.get_log_enable.assert_awaited_once_with(11)
    first_call = logs.tanjunLocalizer.localize.call_args_list[0]
    assert first_call.args[0] == "de-DE"


def test_logs_preferred_locale_guards_use_matching_source_object() -> None:
    source = (Path(__file__).resolve().parents[3] / "extensions" / "logs.py").read_text(encoding="utf-8")
    mismatches: list[str] = []
    for line in source.splitlines():
        if "preferred_locale" not in line or "hasattr(" not in line:
            continue
        match = PREFERRED_LOCALE_GUARD_PATTERN.search(line)
        if not match:
            continue
        true_expr = match.group("true").strip()
        if "=" in true_expr:
            true_expr = true_expr.split("=", 1)[1].strip()
        guard_obj = match.group("obj").strip()
        if not (
            true_expr == guard_obj
            or true_expr.startswith(f"{guard_obj}.")
            or true_expr.startswith(f"str({guard_obj}.")
        ):
            mismatches.append(line.strip())
    assert not mismatches
