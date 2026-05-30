#!/usr/bin/env python3
"""Upgrade all *_generated.py tests to behavioral split tests or delete if redundant."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.helpers.command_profiles import (
    build_call_expr,
    generate_deep_tests,
    hand_written_candidates,
)


def parse_generated(path: Path) -> tuple[str, str] | None:
    text = path.read_text()
    m = re.search(r"from ([\w.]+) import (\w+) as command_fn", text)
    if not m:
        return None
    return m.group(1), m.group(2)


def main() -> None:
    deleted = migrated = 0
    for gen in sorted((ROOT / "tests").rglob("*_generated.py")):
        parsed = parse_generated(gen)
        if not parsed:
            print(f"SKIP {gen}")
            continue
        mod_path, func_name = parsed
        hand = hand_written_candidates(gen)
        if hand:
            gen.unlink()
            deleted += 1
            print(f"DELETE {gen.relative_to(ROOT)} -> {hand[0].relative_to(ROOT)}")
            continue
        call_expr, needs_ctx = build_call_expr(mod_path, func_name)
        out = gen.parent / f"{gen.stem.replace('_generated', '')}.py"
        out.write_text(generate_deep_tests(mod_path, func_name, call_expr, needs_ctx=needs_ctx))
        gen.unlink()
        migrated += 1
        print(f"MIGRATE {gen.relative_to(ROOT)} -> {out.name}")

    games_cov = ROOT / "tests/integration/commands/games/test_games_commands_coverage.py"
    if games_cov.exists() and "except Exception" in games_cov.read_text():
        games_cov.write_text(
            '''from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from commands.games import connect4, tic_tac_toe, wordle
from tests.helpers.assertions import assert_command_responded
from tests.helpers.discord import make_member, make_target_member


pytestmark = [pytest.mark.asyncio, pytest.mark.integration]


async def test_wordle_responds(admin_command_info):
    await wordle(admin_command_info, "en")
    assert_command_responded(admin_command_info)


@patch("commands.games.tic_tac_toe.TicTacToeView", create=True)
async def test_tic_tac_toe_starts(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    with patch("commands.games.tic_tac_toe.discord"):
        await tic_tac_toe.tic_tac_toe(admin_command_info, admin_command_info.user, make_target_member())
    assert_command_responded(admin_command_info)


@patch("commands.games.connect4.Connect4View", create=True)
async def test_connect4_starts(mock_view, admin_command_info):
    mock_view.return_value = MagicMock()
    with patch("commands.games.connect4.discord"):
        await connect4.connect4(admin_command_info, admin_command_info.user, make_member(), 7, 6)
    assert_command_responded(admin_command_info)
'''
        )
        print("FIXED test_games_commands_coverage.py")

    print(f"Done: migrated={migrated} deleted={deleted}")


if __name__ == "__main__":
    main()
