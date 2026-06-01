from __future__ import annotations

import inspect
import types
from collections.abc import Callable
from typing import Any

from diagnostics.kwargs_defaults import build_kwargs_for_handler
from diagnostics.mocks import make_guild, make_interaction, make_member, make_text_channel


async def invoke_interaction_command(
    handler: Callable[..., Any],
    *,
    owner: Any | None = None,
    user: Any | None = None,
    guild: Any | None = None,
    channel: Any | None = None,
    extra_kwargs: dict[str, Any] | None = None,
) -> Any:
    guild = guild or make_guild()
    channel = channel or make_text_channel(guild=guild)
    user = user or make_member(guild=guild)
    interaction = make_interaction(user=user, guild=guild, channel=channel)
    interaction.channel = channel

    call_target = getattr(handler, "callback", handler)
    if getattr(handler, "callback", None) is not None and owner is not None:
        call_target = types.MethodType(call_target, owner)

    kwargs = build_kwargs_for_handler(call_target)
    kwargs["interaction"] = interaction
    kwargs["ctx"] = interaction
    if extra_kwargs:
        kwargs.update(extra_kwargs)

    try:
        sig = inspect.signature(call_target)
        allowed = {k: v for k, v in kwargs.items() if k in sig.parameters}
    except (TypeError, ValueError):
        allowed = {"interaction": interaction, **(extra_kwargs or {})}

    await call_target(**allowed)
    return interaction
