from __future__ import annotations

from typing import Any

from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.fun_assertions import assert_fun_embed_fields
from tests.helpers.fun_matrix import FunMatrixCase, MESSAGE_VARIANTS


def _as_fun_case(case: MatrixCase) -> FunMatrixCase:
    return FunMatrixCase(
        action=case.dimension("action"),
        message_kind=case.dimension("message_kind", "none"),
        permission_profile=case.dimension("permission", "admin"),  # type: ignore[arg-type]
        locale=case.dimension("locale", "en-US"),
        gif_returns=case.dimension("gif", "gif") != "no-gif",
    )


def assert_fun_embed(embed: Any, case: MatrixCase, *, actor_name: str, target_name: str) -> None:
    fun_case = _as_fun_case(case)
    assert_fun_embed_fields(embed, fun_case, actor_name=actor_name, target_name=target_name)
