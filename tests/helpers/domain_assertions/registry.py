from __future__ import annotations

from typing import Any, Callable

from tests.helpers.command_matrix.harness import _assert_profile_for_group
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.admin import assert_admin_embed
from tests.helpers.domain_assertions.ai import assert_ai_embed
from tests.helpers.domain_assertions.base import (
    assert_default_embed,
    assert_live_response_outcome,
    assert_no_error_markers,
)
from tests.helpers.domain_assertions.channel import assert_channel_embed
from tests.helpers.domain_assertions.fun import assert_fun_embed
from tests.helpers.domain_assertions.games import assert_games_embed
from tests.helpers.domain_assertions.giveaway import assert_giveaway_embed
from tests.helpers.domain_assertions.image import assert_image_embed
from tests.helpers.domain_assertions.level import assert_level_embed
from tests.helpers.domain_assertions.logs import assert_logs_embed
from tests.helpers.domain_assertions.math import assert_math_embed
from tests.helpers.domain_assertions.minigames import assert_minigame_embed
from tests.helpers.domain_assertions.setup import assert_setup_embed
from tests.helpers.domain_assertions.utility import assert_utility_embed

EmbedAssertFn = Callable[[Any, MatrixCase], None]

EMBED_ASSERTIONS: dict[str, EmbedAssertFn] = {
    "default": assert_default_embed,
    "fun": lambda e, c: None,
    "math": assert_math_embed,
    "admin": assert_admin_embed,
    "games": assert_games_embed,
    "ai": assert_ai_embed,
    "utility": assert_utility_embed,
    "level": assert_level_embed,
    "giveaway": assert_giveaway_embed,
    "image": assert_image_embed,
    "channel": assert_channel_embed,
    "logs": assert_logs_embed,
    "minigame": assert_minigame_embed,
    "setup": assert_setup_embed,
}


def assert_matrix_embed(embed: Any, case: MatrixCase, *, actor_name: str = "", target_name: str = "") -> None:
    profile = _assert_profile_for_group(case.group)
    if profile == "setup":
        profile = "setup"
    if profile == "fun":
        assert_fun_embed(embed, case, actor_name=actor_name or "Actor", target_name=target_name or "Target")
        return
    fn = EMBED_ASSERTIONS.get(profile, assert_default_embed)
    fn(embed, case)


def assert_matrix_live_response(result: dict[str, Any], case: MatrixCase, *, session: Any) -> None:
    if assert_live_response_outcome(result, case):
        return
    embed = result.get("embed")
    content = result.get("content") or ""
    if embed is not None:
        assert_matrix_embed(
            embed,
            case,
            actor_name=getattr(session, "user_username", "Actor"),
            target_name=getattr(session, "bot_username", "Target")
            if case.dimension("target") == "bot"
            else getattr(session, "user_username", "Actor"),
        )
        return
    assert content.strip(), f"empty live response for {case.id}"
    assert_no_error_markers(content, case_id=case.id)
