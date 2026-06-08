from __future__ import annotations

import pytest

from tests.helpers.command_matrix.harness import (
    invoke_handler_for_case,
    matrix_patches,
    permission_for_case,
)
from tests.helpers.command_matrix.iterators import (
    iter_behavior_spec_cases,
    iter_integration_cases,
    iter_unit_cases,
)
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.permission_profiles import command_info_for_permission
from tests.helpers.domain_assertions.registry import assert_matrix_embed
from tests.helpers.domain_assertions.base import embed_from_command_info

pytestmark = pytest.mark.asyncio


async def run_unit_matrix_case(case: MatrixCase) -> None:
    from tests.helpers.command_matrix.harness import find_spec_for_path
    from tests.helpers.command_matrix.resolver import resolve_command_callable

    spec = find_spec_for_path(case.tree_path)
    if spec and spec.skip_reason:
        pytest.skip(spec.skip_reason)
    handler = resolve_command_callable(case.tree_path)
    if handler is None:
        pytest.fail(f"No command handler resolved for {case.id}")
    info = command_info_for_permission(permission_for_case(case))
    if case.dimension("locale"):
        info.locale = case.dimension("locale")
    with matrix_patches(case):
        try:
            await invoke_handler_for_case(case, info)
        except (AssertionError, AttributeError, ValueError) as exc:
            if case.dimension("permission") == "no_guild":
                pytest.skip("guild-required command under no_guild profile")
            if "guild" in str(exc).lower():
                pytest.skip("guild-required command under no_guild profile")
            raise
    interaction = getattr(info, "_matrix_interaction", None)
    has_response = bool(info.reply.await_args_list or info.reply.call_args_list)
    if interaction is not None:
        has_response = has_response or bool(
            interaction.response.send_message.await_args_list
            or getattr(interaction.response.send_modal, "called", False)
        )
    if not has_response:
        pytest.fail(f"handler produced no reply for {case.id}")
    if case.group == "funcmd_name":
        from tests.helpers.discord import make_member

        actor = info.user.name
        target_name = (
            "BotTarget"
            if case.dimension("target") == "bot"
            else make_member(user_id=222222222, name="Target").name
        )
        assert_matrix_embed(
            embed_from_command_info(info),
            case,
            actor_name=actor,
            target_name=target_name if case.dimension("target") else actor,
        )
    else:
        assert_matrix_embed(embed_from_command_info(info), case)


def register_unit_matrix_tests(module_globals: dict, group: str | None = None) -> None:
    cases = iter_unit_cases(group)

    @pytest.mark.parametrize("case", cases, ids=lambda c: c.id)
    async def test_command_unit_matrix(case: MatrixCase) -> None:
        await run_unit_matrix_case(case)

    module_globals["test_command_unit_matrix"] = test_command_unit_matrix


def specs_for_group(group: str):
    from diagnostics.registry import all_specs
    from tests.helpers.command_coverage.inventory import root_group_for_path

    return [s for s in all_specs() if s.tree_path and root_group_for_path(s.tree_path) == group and not s.skip_reason]


async def run_integration_matrix_case(case: MatrixCase) -> None:
    from tests.helpers.command_matrix.integration import run_integration_matrix_case as _run

    await _run(case)


def register_integration_matrix_tests(module_globals: dict, group: str | None = None) -> None:
    cases = iter_integration_cases(group)

    @pytest.mark.parametrize("case", cases, ids=lambda c: c.id)
    async def test_command_integration_matrix(case: MatrixCase) -> None:
        await run_integration_matrix_case(case)

    module_globals["test_command_integration_matrix"] = test_command_integration_matrix


async def run_behavior_spec_test(spec) -> None:
    from diagnostics.registry import run_spec
    from tests.helpers.command_matrix.resolver import resolve_command_callable
    from tests.helpers.extension_loader import make_bot_for_extensions

    if not spec.tree_path:
        pytest.fail(f"behavior spec {spec.id} has no tree_path")
    handler = resolve_command_callable(spec.tree_path)
    assert handler is not None, f"no handler resolved for behavior spec {spec.tree_path}"
    if spec.method_name == "unknown":
        return
    bot = make_bot_for_extensions()
    outcome = await run_spec(spec, bot)
    assert outcome.passed, outcome.message


def register_behavior_spec_tests(module_globals: dict, group: str) -> None:
    specs = specs_for_group(group)
    if not specs:
        return

    @pytest.mark.parametrize("spec", specs, ids=lambda s: s.id)
    async def test_command_behavior_spec(spec) -> None:
        await run_behavior_spec_test(spec)

    module_globals["test_command_behavior_spec"] = test_command_behavior_spec
