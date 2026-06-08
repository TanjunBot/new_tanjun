#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))

from diagnostics.tree import load_manifest

_MANIFEST_ROOTS = load_manifest()["roots"]

DOMAIN_GROUPS: dict[str, list[str]] = {
    "admin": [g for g in _MANIFEST_ROOTS if g.startswith("admin_")],
    "math": ["math_name"],
    "utility": ["utility_help_name", "utilitycmd_name", "utility_scheduledmessage_name"],
    "channel": ["channel_name"],
    "ai": ["ai_name"],
    "games": ["games_name"],
    "giveaway": ["giveaway_name"],
    "image": ["image_name"],
    "level": [g for g in _MANIFEST_ROOTS if g.startswith("level_")],
    "logs": ["logs_name"],
    "minigames": ["minigame_name"],
    "setup": ["setup_name"],
}


def _unit_template(domain: str, groups: list[str]) -> str:
    groups_repr = repr(groups)
    return f'''from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_unit_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_unit_matrix_case

pytestmark = pytest.mark.asyncio


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in {groups_repr}:
        cases.extend(iter_unit_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_{domain}_unit_matrix(case: MatrixCase) -> None:
    await run_unit_matrix_case(case)
'''


def _e2e_template(domain: str, groups: list[str]) -> str:
    groups_repr = repr(groups)
    return f'''from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_e2e_live_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.registry import assert_matrix_live_response
from tests.helpers.live_discord.session import LiveGuildSession

pytestmark = [
    pytest.mark.live_discord,
    pytest.mark.live_e2e,
    pytest.mark.live_domain,
    pytest.mark.slow,
    pytest.mark.asyncio,
]


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in {groups_repr}:
        cases.extend(iter_e2e_live_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_{domain}_slash_command_live(case: MatrixCase, live_guild_session: LiveGuildSession) -> None:
    result = await live_guild_session.run_matrix_case(case)
    assert_matrix_live_response(result, case, session=live_guild_session)
'''


def _integration_template(domain: str, groups: list[str]) -> str:
    groups_repr = repr(groups)
    return f'''from __future__ import annotations

import pytest

from tests.helpers.command_matrix.iterators import iter_integration_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.command_matrix.test_runners import run_integration_matrix_case

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]


def _cases() -> list[MatrixCase]:
    cases: list[MatrixCase] = []
    for group in {groups_repr}:
        cases.extend(iter_integration_cases(group))
    return cases


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c.id)
async def test_{domain}_integration_matrix(case: MatrixCase) -> None:
    await run_integration_matrix_case(case)
'''


def _behavior_template(domain: str, groups: list[str]) -> str:
    groups_repr = repr(groups)
    return f'''from __future__ import annotations

import pytest

from diagnostics.registry import all_specs
from tests.helpers.command_coverage.inventory import root_group_for_path
from tests.helpers.command_matrix.test_runners import run_behavior_spec_test

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

_GROUPS = {groups_repr}


def _specs():
    return [
        s
        for s in all_specs()
        if s.tree_path and root_group_for_path(s.tree_path) in _GROUPS and not s.skip_reason
    ]


@pytest.mark.parametrize("spec", _specs(), ids=lambda s: s.id)
async def test_{domain}_behavior_spec(spec) -> None:
    await run_behavior_spec_test(spec)
'''


def main() -> None:
    for domain, groups in DOMAIN_GROUPS.items():
        unit_dir = ROOT / "tests" / "unit" / "commands" / domain
        unit_dir.mkdir(parents=True, exist_ok=True)
        (unit_dir / f"test_{domain}_matrix.py").write_text(_unit_template(domain, groups), encoding="utf-8")

        int_dir = ROOT / "tests" / "integration" / "commands" / domain
        int_dir.mkdir(parents=True, exist_ok=True)
        (int_dir / f"test_{domain}_matrix.py").write_text(
            _integration_template(domain, groups), encoding="utf-8"
        )
        (int_dir / f"test_{domain}_behavior_specs.py").write_text(
            _behavior_template(domain, groups), encoding="utf-8"
        )

        e2e_dir = ROOT / "tests" / "e2e_live" / domain
        e2e_dir.mkdir(parents=True, exist_ok=True)
        (e2e_dir / "__init__.py").write_text("", encoding="utf-8")
        (e2e_dir / f"test_{domain}_commands_live.py").write_text(_e2e_template(domain, groups), encoding="utf-8")

    print(f"Generated domain matrix tests for {len(DOMAIN_GROUPS)} domains")


if __name__ == "__main__":
    main()
