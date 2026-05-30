from __future__ import annotations

import inspect
import types
from collections.abc import Callable
from typing import Any
from unittest.mock import MagicMock

from tests.helpers.discord import make_guild, make_interaction, make_member, make_text_channel


def make_log_enable(**flags: bool) -> MagicMock:
    enable = MagicMock()
    for key, value in flags.items():
        setattr(enable, key, value)
    if not flags:
        for name in (
            "automod_rule_create",
            "automod_rule_update",
            "automod_rule_delete",
            "automod_action",
            "guild_channel_delete",
            "guild_channel_create",
            "guild_channel_update",
            "guild_update",
            "invite_create",
            "invite_delete",
            "member_join",
            "member_remove",
            "member_update",
            "user_update",
            "member_ban",
            "member_unban",
            "presence_update",
            "message_edit",
            "message_delete",
            "reaction_add",
            "reaction_remove",
            "guild_role_create",
            "guild_role_delete",
            "guild_role_update",
        ):
            setattr(enable, name, True)
    return enable


def iter_app_command_methods(obj: Any) -> list[tuple[str, Callable[..., Any]]]:
    methods: list[tuple[str, Callable[..., Any]]] = []
    for name, member in inspect.getmembers(obj, predicate=inspect.ismethod):
        if name.startswith("_"):
            continue
        if not inspect.iscoroutinefunction(member):
            continue
        if name in ("log_consumer_task",):
            continue
        methods.append((name, member))
    for name, fn_member in inspect.getmembers(type(obj), predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        if not inspect.iscoroutinefunction(fn_member):
            continue
        bound = getattr(obj, name, None)
        if bound is None or (name, bound) in methods:  # type: ignore[comparison-overlap]
            continue
        methods.append((name, bound))
    return methods


async def invoke_interaction_command(
    handler: Callable[..., Any],
    *,
    owner: Any | None = None,
    user: MagicMock | None = None,
    guild: MagicMock | None = None,
    channel: MagicMock | None = None,
    extra_kwargs: dict[str, Any] | None = None,
) -> MagicMock:
    guild = guild or make_guild()
    channel = channel or make_text_channel(guild=guild)
    user = user or make_member()
    interaction = make_interaction(user=user, guild=guild, channel=channel)
    kwargs: dict[str, Any] = {"ctx": interaction, "interaction": interaction}
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    call_target = getattr(handler, "callback", handler)
    if getattr(handler, "callback", None) is not None and owner is not None:
        call_target = types.MethodType(call_target, owner)
    try:
        sig = inspect.signature(call_target)
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
    except (TypeError, ValueError):
        allowed = {"interaction": interaction, **(extra_kwargs or {})}

    try:
        await call_target(**allowed)
    except TypeError:
        fallback = {"ctx": interaction, **(extra_kwargs or {})}
        await call_target(**fallback)
    return interaction


def make_automod_rule(guild: MagicMock | None = None) -> MagicMock:
    guild = guild or make_guild()
    rule = MagicMock()
    rule.id = 1
    rule.name = "test-rule"
    rule.enabled = True
    rule.guild = guild
    rule.channel_id = 444444444
    rule.creator = make_member()
    rule.creator.mention = "<@111>"
    rule.trigger = MagicMock()
    rule.trigger.type = 1
    rule.trigger.keyword_filter = ["bad"]
    rule.trigger.regex_patterns = []
    rule.trigger.presets = MagicMock(profanity=True, sexual_content=False, slurs=False)
    rule.trigger.allow_list = []
    rule.trigger.mention_limit = None
    rule.trigger.mention_raid_protection = False
    rule.exempt_roles = []
    rule.exempt_channels = []
    rule.actions = []
    guild.audit_logs = MagicMock(return_value=_empty_async_iter())
    return rule


def _empty_async_iter() -> Any:
    async def _gen() -> Any:  # type: ignore[misc]
        if False:
            yield

    return _gen()


def make_audit_log_entry(user: MagicMock | None = None, target_id: int = 1) -> MagicMock:
    entry = MagicMock()
    entry.user = user or make_member()
    entry.user.mention = "<@111>"
    entry.target = MagicMock(id=target_id)
    return entry


def async_audit_logs(*entries: MagicMock) -> Any:
    async def _gen() -> Any:  # type: ignore[misc]
        for e in entries:
            yield e

    return _gen()
