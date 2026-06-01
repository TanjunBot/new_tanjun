from __future__ import annotations

import asyncio
import inspect
from contextlib import ExitStack
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from diagnostics.models import CheckOutcome
from diagnostics.patches import extension_patches
from diagnostics.strict_skips import PREFIX_COMMANDS_EXCLUDED_SET, PREFIX_SKIP_ALLOWLIST


def _admin_author_id() -> int:
    try:
        import config

        if config.adminIds:
            return int(config.adminIds[0])
    except Exception:
        pass
    return 1001


def _build_prefix_kwargs(callback: Any) -> dict[str, Any]:
    from diagnostics.kwargs_defaults import build_kwargs_for_handler

    return build_kwargs_for_handler(callback)


async def _invoke_prefix_command(cog: Any, command: Any, bot: Any) -> None:
    from diagnostics.mocks import make_guild, make_member, make_text_channel

    guild = make_guild()
    channel = make_text_channel(guild=guild)
    author = make_member(user_id=_admin_author_id(), guild=guild)
    ctx: Any = type("Ctx", (), {})()
    ctx.author = author
    ctx.guild = guild
    ctx.channel = channel
    ctx.bot = bot
    status_message = MagicMock()
    status_message.edit = AsyncMock()
    ctx.send = AsyncMock(return_value=status_message)
    ctx.message = type("Msg", (), {"attachments": [], "content": "diag", "guild": guild})()

    kwargs = _build_prefix_kwargs(command.callback)
    params = list(inspect.signature(command.callback).parameters)
    if params and params[0] == "self":
        await command.callback(cog, ctx, **kwargs)
    else:
        await command.callback(ctx, **kwargs)


async def run_prefix_command_checks(bot: Any) -> list[CheckOutcome]:
    outcomes: list[CheckOutcome] = []
    try:
        from extensions.administration import AdministrationCog
    except ImportError as exc:
        return [CheckOutcome("prefix.administration", False, str(exc))]

    cog = bot.cogs.get("AdministrationCog")
    if cog is None:
        try:
            cog = AdministrationCog(bot)
        except Exception as exc:
            return [CheckOutcome("prefix.administration", False, f"Could not instantiate cog: {exc}")]

    commands_list = sorted(cog.get_commands(), key=lambda c: c.name)
    if not commands_list:
        return [CheckOutcome("prefix.administration", False, "No prefix commands discovered")]

    for command in commands_list:
        name = command.name
        check_id = f"prefix.admin.{name}"
        if name in PREFIX_COMMANDS_EXCLUDED_SET:
            reason = PREFIX_SKIP_ALLOWLIST.get(name, "Excluded prefix command")
            outcomes.append(CheckOutcome(check_id, True, reason, skipped=True, skip_allowed=True))
            continue
        try:
            with extension_patches("extensions.administration"):
                with ExitStack() as stack:
                    if name == "bsaccdata":
                        stack.enter_context(
                            patch.object(
                                cog,
                                "getAccData",
                                AsyncMock(return_value={"brawlers": [{}, {}]}),
                            )
                        )
                    if name == "sync":
                        tree = getattr(bot, "tree", None)
                        if tree is None:
                            tree = MagicMock()
                            bot.tree = tree
                        tree.walk_commands = MagicMock(return_value=[])
                        tree.sync = AsyncMock(return_value=[])
                    await asyncio.wait_for(_invoke_prefix_command(cog, command, bot), timeout=30.0)
        except TimeoutError:
            outcomes.append(CheckOutcome(check_id, False, "Timed out after 30s"))
        except Exception as exc:
            outcomes.append(CheckOutcome(check_id, False, str(exc)))
        else:
            outcomes.append(CheckOutcome(check_id, True, "OK"))

    return outcomes
