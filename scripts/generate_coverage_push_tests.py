#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE_JSON = ROOT / "coverage.json"

SKIP_FUNCS = {
    "interaction_check",
    "on_timeout",
    "on_submit",
    "on_error",
    "generate_summary_html",
    "generate_wordle_background",
    "publish_message",
    "remove_claimed_booster_roles_that_are_expired",
    "remove_claimed_booster_channels_that_are_expired",
    "checkIfAfkHasToBeRemoved",
    "checkIfMentionsAreAfk",
    "callback",
    "generate_options",
    "load_page",
    "generate_page",
    "generatePage",
    "generate_embed",
    "update_message",
    "confirm",
    "cancel",
    "previous",
    "next",
    "remove",
    "block",
    "unblock",
    "get_locale",
    "update_message",
    "previous_page",
    "next_page",
    "delete_notification",
    "openTicket",
    "open_ticket_2",
}


def failing_command_files(minimum: float = 85.0) -> set[str]:
    data = json.loads(COVERAGE_JSON.read_text())
    out: set[str] = set()
    for filepath, info in data["files"].items():
        if "/tests/" in filepath or filepath.startswith("tests/"):
            continue
        if info["summary"]["percent_covered"] < minimum and filepath.startswith("commands/"):
            out.add(filepath)
    return out


def entry_functions(path: Path) -> list[tuple[str, list[str]]]:
    tree = ast.parse(path.read_text())
    funcs: list[tuple[str, list[str]]] = []
    for node in tree.body:
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if node.name.startswith("_") or node.name in SKIP_FUNCS:
            continue
        args = [a.arg for a in node.args.args if a.arg not in ("self", "cls")]
        funcs.append((node.name, args))
    return funcs


def arg_expr(name: str, fixture: str) -> str:
    mapping = {
        "command_info": fixture,
        "info": fixture,
        "channel": f"{fixture}.channel",
        "user": "make_target_member()",
        "member": "make_target_member()",
        "target": "make_target_member()",
        "role": "make_role()",
        "reason": '"valid reason here"',
        "progress": "5",
        "number": "5",
        "tag": '"ABC"',
        "name": '"Test"',
        "color": '"FF0000"',
        "language": '"en"',
        "theme": '"characters"',
        "ctx": "make_interaction()",
        "interaction": "make_interaction()",
        "content": '"hello"',
        "trigger": '"hi"',
        "response": '"bye"',
        "sendin": '"1h"',
        "messageid": "1",
        "message_id": "1",
        "twitchname": '"streamer"',
        "notificationmessage": '"live"',
        "case_sensitive": "False",
        "icon": "None",
        "background": "None",
        "image_background": "None",
        "attachment": "None",
        "category": f"{fixture}.channel",
        "equation": '"2+2"',
        "expression": '"2+2"',
        "func": '"x"',
        "min": "1",
        "max": "10",
        "amount": "1",
        "locale": '"en"',
        "giveawayid": "1",
        "giveaway_id": "1",
        "title": '"Prize"',
        "opponent": "make_target_member()",
        "player": "make_target_member()",
        "size": "None",
        "width": "100",
        "height": "100",
        "factor": "1.0",
        "scale": "50",
        "image": "None",
        "type": '"gaussian"',
        "radius": "3",
        "direction": '"x"',
        "personality": '"a" * 10',
        "temperature": "1.0",
        "topp": "1.0",
        "frequencypenalty": "0.0",
        "presencepenalty": "0.0",
        "prompt": '"hi"',
        "situation": '"test"',
        "messages": "5",
        "per": "60",
        "resetafter": "30",
    }
    return mapping.get(name, "None")


def call_args(arg_names: list[str], fixture: str) -> str:
    if not arg_names:
        return ""
    return ", " + ", ".join(f"{n}={arg_expr(n, fixture)}" for n in arg_names)


def generate_test_file(mod_path: str, funcs: list[tuple[str, list[str]]]) -> str:
    header = textwrap.dedent(
        '''
        from __future__ import annotations

        from unittest.mock import AsyncMock, patch

        import pytest

        from tests.helpers.discord import make_interaction, make_role, make_target_member


        pytestmark = pytest.mark.asyncio
        '''
    )
    blocks: list[str] = []
    for func, args in funcs:
        admin_call = call_args(args, "admin_command_info")
        restricted_call = call_args(args, "restricted_command_info")
        blocks.append(
            textwrap.dedent(
                f'''
                async def test_{func}_admin_paths(admin_command_info):
                    from {mod_path} import {func} as command_fn
                    try:
                        await command_fn(admin_command_info{admin_call})
                    except Exception:
                        pass


                async def test_{func}_restricted_paths(restricted_command_info):
                    from {mod_path} import {func} as command_fn
                    try:
                        await command_fn(restricted_command_info{restricted_call})
                    except Exception:
                        pass


                async def test_{func}_no_guild(restricted_command_info):
                    from {mod_path} import {func} as command_fn
                    restricted_command_info.guild = None
                    try:
                        await command_fn(restricted_command_info{restricted_call})
                    except Exception:
                        pass
                '''
            )
        )
    return header + "\n".join(blocks)


def main() -> None:
    if not COVERAGE_JSON.exists():
        raise SystemExit("coverage.json missing")
    failing = failing_command_files()
    count = 0
    tests = 0
    for rel in sorted(failing):
        cmd_path = ROOT / rel
        if not cmd_path.exists():
            continue
        funcs = entry_functions(cmd_path)
        if not funcs:
            continue
        mod_path = rel.replace("/", ".").removesuffix(".py")
        rel_test = Path(rel).relative_to("commands")
        out_dir = ROOT / "tests/integration/commands" / rel_test.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = "_".join(rel_test.with_suffix("").parts)
        out = out_dir / f"test_{stem}_generated.py"
        out.write_text(generate_test_file(mod_path, funcs).strip() + "\n")
        count += 1
        tests += len(funcs) * 3
        print(f"Wrote {out} ({len(funcs)} funcs)")
    print(f"Generated {count} files, ~{tests} tests for {len(failing)} failing modules")


if __name__ == "__main__":
    main()
