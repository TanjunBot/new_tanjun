from __future__ import annotations

import ast
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[2]

ARG_DEFAULTS = {
    "command_info": "info",
    "info": "info",
    "channel": "info.channel",
    "category": "info.channel",
    "user": "make_target_member()",
    "member": "make_target_member()",
    "target": "make_target_member()",
    "role": "make_role()",
    "ctx": "ctx",
    "interaction": "make_interaction()",
    "reason": '"test reason"',
    "progress": "5",
    "number": "5",
    "name": '"Test"',
    "color": "None",
    "icon": "None",
    "language": '"en"',
    "theme": '"characters"',
    "content": '"hello"',
    "message_id": "1",
    "messageid": "1",
    "twitchname": '"streamer"',
    "notificationmessage": '"live"',
    "sendin": '"1h"',
    "equation": '"2+2"',
    "expression": '"2+2"',
    "giveaway_id": "1",
    "title": '"Prize"',
    "opponent": "make_target_member()",
    "player": "make_target_member()",
    "player_tag": "None",
    "attachment": "None",
    "image": "None",
    "type": '"gaussian"',
    "radius": "3",
    "width": "100",
    "height": "100",
    "scale": "50",
    "factor": "1.0",
    "func": '"x"',
    "min": "1",
    "max": "10",
    "amount": "1",
    "locale": '"en"',
    "messages": "5",
    "per": "60",
    "resetafter": "30",
    "situation": '"test"',
    "prompt": '"hi"',
    "locale_key_prefix": '"minigames.test"',
}


class ProfileKind(Enum):
    BOOSTER_ADMIN = "booster_admin"
    COUNTING_MOD = "counting_mod"
    WORDCHAIN = "wordchain"
    BRAWLSTARS = "brawlstars"
    FEEDBACK_MODAL = "feedback_modal"
    PERMISSION_HELPER = "permission_helper"
    GENERIC = "generic"


@dataclass
class CommandProfile:
    kind: ProfileKind
    mod_path: str
    func_name: str
    call_expr: str
    silent_no_guild: bool = False
    needs_ctx: bool = False
    admin_checks: list[str] = field(default_factory=list)

    @classmethod
    def from_module(cls, mod_path: str, func_name: str, call_expr: str) -> CommandProfile:
        rel = mod_path.replace(".", "/") + ".py"
        source = (ROOT / rel).read_text() if (ROOT / rel).exists() else ""
        kind = ProfileKind.GENERIC
        silent_no_guild = False
        needs_ctx = "ctx" in call_expr
        if func_name == "require_moderate_members":
            kind = ProfileKind.PERMISSION_HELPER
            silent_no_guild = True
        elif "booster_service" in source or "BoosterType" in source:
            if func_name.startswith("claim"):
                kind = ProfileKind.GENERIC
            else:
                kind = ProfileKind.BOOSTER_ADMIN
        elif "CountingRepository" in source:
            kind = ProfileKind.COUNTING_MOD
            silent_no_guild = True
        elif "wordchain" in mod_path:
            kind = ProfileKind.WORDCHAIN
            silent_no_guild = True
        elif "brawlstars" in source or "get_brawlstars" in source:
            kind = ProfileKind.BRAWLSTARS
        elif func_name == "feedback" or "FeedbackModal" in source:
            kind = ProfileKind.FEEDBACK_MODAL
            needs_ctx = True
        return cls(kind, mod_path, func_name, call_expr, silent_no_guild, needs_ctx)


def build_call_expr(mod_path: str, func_name: str) -> tuple[str, bool]:
    path = ROOT / (mod_path.replace(".", "/") + ".py")
    tree = ast.parse(path.read_text())
    parts: list[str] = []
    needs_ctx = False
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
            params = [a for a in node.args.args if a.arg not in ("self", "cls")]
            for i, param in enumerate(params):
                if i == 0 and param.arg in ("command_info", "info"):
                    parts.append("info")
                    continue
                if param.arg == "ctx":
                    parts.append("ctx")
                    needs_ctx = True
                    continue
                parts.append(f"{param.arg}={ARG_DEFAULTS.get(param.arg, 'None')}")
            break
    return ", ".join(parts), needs_ctx


@contextmanager
def profile_patches(profile: CommandProfile, *, ctx: Any | None = None) -> Iterator[dict[str, AsyncMock]]:
    mocks: dict[str, AsyncMock] = {}
    stack: list[Any] = []
    rel = profile.mod_path.replace(".", "/") + ".py"
    source = (ROOT / rel).read_text() if (ROOT / rel).exists() else ""

    def _enter(p: Any) -> Any:
        stack.append(p)
        return p.__enter__()

    _enter(patch("api.execute_query", new_callable=AsyncMock, return_value=[]))
    _enter(patch("api.execute_action", new_callable=AsyncMock, return_value=0))
    _enter(patch("api.safe_execute_query", new_callable=AsyncMock, return_value=[]))
    _enter(patch("api.execute_insert_and_get_id", new_callable=AsyncMock, return_value=1))

    if profile.kind == ProfileKind.BOOSTER_ADMIN:
        svc = _enter(patch(f"{profile.mod_path}.booster_service"))
        svc.get = AsyncMock(return_value=None)
        svc.add = AsyncMock()
        svc.remove = AsyncMock()
        svc.get_claim_for_user = AsyncMock(return_value=None)
        svc.claim = AsyncMock(return_value=True)
        mocks.update({"get": svc.get, "add": svc.add, "remove": svc.remove, "claim": svc.claim})

    if profile.kind == ProfileKind.COUNTING_MOD:
        _enter(patch(f"{profile.mod_path}.require_moderate_members", side_effect=_counting_require_side_effect))
        if "require_bot_permissions" in source:
            _enter(patch(f"{profile.mod_path}.require_bot_permissions", new_callable=AsyncMock, return_value=False))
        if "require_counting_channel" in source:
            _enter(patch(f"{profile.mod_path}.require_counting_channel", new_callable=AsyncMock, return_value=0))
        if "require_valid_progress" in source:
            _enter(patch(f"{profile.mod_path}.require_valid_progress", new_callable=AsyncMock, return_value=False))
        repo = _enter(patch(f"{profile.mod_path}._repo"))
        repo.set_progress = AsyncMock()
        repo.set_challenge_progress = AsyncMock()
        repo.set_mode_progress = AsyncMock()
        repo.get_progress = AsyncMock(return_value=0)
        repo.remove_channel = AsyncMock()
        repo.clear = AsyncMock()
        mocks["set_progress"] = repo.set_progress

    if profile.kind == ProfileKind.WORDCHAIN:
        if "set_wordchain_word" in source:
            _enter(patch(f"{profile.mod_path}.set_wordchain_word", new_callable=AsyncMock))
        if "remove_wordchain" in source:
            _enter(patch(f"{profile.mod_path}.remove_wordchain", new_callable=AsyncMock))

    if profile.kind == ProfileKind.BRAWLSTARS:
        _enter(patch(f"{profile.mod_path}.get_brawlstars_linked_account", new_callable=AsyncMock, return_value="#TEST"))
        svc = _enter(patch(f"{profile.mod_path}.get_brawlstars_service"))
        instance = MagicMock()
        instance.get_player = AsyncMock(return_value=MagicMock(tag="#ABC", name="Player"))
        instance.get_battle_log = AsyncMock(return_value=[])
        instance.get_brawlers = AsyncMock(return_value={"items": []})
        svc.return_value = instance

    if profile.kind == ProfileKind.FEEDBACK_MODAL:
        _enter(patch(f"{profile.mod_path}.feedbackIsBlocked", new_callable=AsyncMock, return_value=False))
        if ctx is not None:
            ctx.response.send_modal = AsyncMock()

    try:
        yield mocks
    finally:
        while stack:
            stack.pop().__exit__(None, None, None)


async def _counting_require_side_effect(command_info: Any, *_args: Any) -> bool:
    if command_info.guild is None:
        return True
    perms = command_info.channel.permissions_for(command_info.user)
    if not getattr(perms, "moderate_members", False):
        await command_info.reply(embed=MagicMock())
        return True
    return False


def hand_written_candidates(generated: Path) -> list[Path]:
    stem = generated.stem.replace("_generated", "")
    parts = stem.removeprefix("test_").split("_")
    candidates: list[Path] = []
    if parts[-1]:
        candidates.append(generated.parent / f"test_{parts[-1]}.py")
    module_tail = stem.removeprefix("test_")
    for prefix in ("utility_", "games_", "math_", "level_", "logs_", "channel_", "ai_", "giveaway_", "admin_"):
        if module_tail.startswith(prefix):
            candidates.append(generated.parent / f"test_{module_tail[len(prefix):]}.py")
    for sub in (
        "utility_brawlstars_",
        "minigames_counting_modes_",
        "minigames_counting_challenge_",
        "minigames_counting_",
        "minigames_wordchain_",
    ):
        if module_tail.startswith(sub):
            candidates.append(generated.parent / f"test_{module_tail[len(sub):]}.py")
    if "brawlstars" in str(generated):
        for name in ("test_brawlstars.py", "test_brawlstars_club_deep.py", "test_brawlstars_events_deep.py"):
            candidates.append(generated.parent / name)
    if "feedback" in stem:
        candidates.append(generated.parent / "test_feedback_deep.py")
    if generated.parent.name == "games":
        candidates.append(generated.parent / "test_games_commands_coverage.py")
    seen: set[Path] = set()
    out: list[Path] = []
    for c in candidates:
        if c not in seen and c != generated and c.exists():
            seen.add(c)
            out.append(c)
    return out


def generate_deep_tests(mod_path: str, func_name: str, call_expr: str, *, needs_ctx: bool) -> str:
    profile = CommandProfile.from_module(mod_path, func_name, call_expr)
    ctx_block = ""
    if needs_ctx:
        ctx_block = "    ctx = MagicMock()\n    ctx.response.send_modal = AsyncMock()\n"
        extra_import = "from unittest.mock import AsyncMock, MagicMock\n"
    else:
        extra_import = "from unittest.mock import AsyncMock\n"
    discord_helpers: list[str] = []
    if "make_role()" in call_expr:
        discord_helpers.append("make_role")
    if "make_target_member()" in call_expr:
        discord_helpers.append("make_target_member")
    discord_import = ""
    if discord_helpers:
        discord_import = f"from tests.helpers.discord import {', '.join(discord_helpers)}\n"
    admin_extra = ""
    if profile.kind in (ProfileKind.COUNTING_MOD, ProfileKind.WORDCHAIN):
        admin_extra = "    info.channel.send = AsyncMock()\n"
    patch_ctx = ", ctx=ctx" if needs_ctx else ""
    mod_r, func_r, call_r = repr(mod_path), repr(func_name), repr(call_expr)
    return f'''"""Integration tests for {mod_path}.{func_name}."""

from __future__ import annotations

{extra_import}{discord_import}import pytest

from tests.helpers.assertions import assert_matrix_outcome
from tests.helpers.command_profiles import CommandProfile, profile_patches


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

PROFILE = CommandProfile.from_module({mod_r}, {func_r}, {call_r})


async def test_{func_name}_restricted(restricted_command_info):
    info = restricted_command_info
{ctx_block}    with profile_patches(PROFILE{patch_ctx}) as mocks:
        from {mod_path} import {func_name} as command_fn
        await command_fn({call_expr})
    assert_matrix_outcome(info, "restricted", PROFILE, mocks)


async def test_{func_name}_no_guild(no_guild_command_info):
    info = no_guild_command_info
{ctx_block}    with profile_patches(PROFILE{patch_ctx}) as mocks:
        from {mod_path} import {func_name} as command_fn
        await command_fn({call_expr})
    assert_matrix_outcome(info, "no_guild", PROFILE, mocks)


async def test_{func_name}_admin(admin_command_info):
    info = admin_command_info
{admin_extra}{ctx_block}    with profile_patches(PROFILE{patch_ctx}) as mocks:
        from {mod_path} import {func_name} as command_fn
        await command_fn({call_expr})
    assert_matrix_outcome(info, "admin", PROFILE, mocks)
'''
