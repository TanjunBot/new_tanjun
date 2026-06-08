from __future__ import annotations

from tests.helpers.fun_assertions import assert_fun_embed_fields
from tests.helpers.fun_matrix import FUN_GROUP_NAME, FunLiveCase, iter_fun_live_cases

__all__ = [
    "FUN_GROUP_NAME",
    "FunLiveCase",
    "assert_fun_embed",
    "iter_fun_cases",
    "iter_fun_live_cases",
]


def iter_fun_cases() -> list[FunLiveCase]:
    return iter_fun_live_cases()


def assert_fun_embed(
    embed: dict,
    case: FunLiveCase,
    *,
    actor_name: str,
    target_name: str,
) -> None:
    from tests.helpers.fun_matrix import FunMatrixCase

    matrix_case = FunMatrixCase(action=case.action, message_kind=case.message_kind)
    assert_fun_embed_fields(
        _dict_embed_adapter(embed),
        matrix_case,
        actor_name=actor_name,
        target_name=target_name,
    )


def _dict_embed_adapter(embed: dict) -> object:
    class _Footer:
        def __init__(self, data: dict) -> None:
            self.text = data.get("text")

    class _Adapter:
        def __init__(self, data: dict) -> None:
            self.title = data.get("title")
            self.description = data.get("description")
            footer = data.get("footer") or {}
            self.footer = _Footer(footer) if footer else None
            image = data.get("image") or {}
            self.image = image.get("url") if image else None

    return _Adapter(embed)
