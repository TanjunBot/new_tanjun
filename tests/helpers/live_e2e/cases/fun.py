from __future__ import annotations

from tests.helpers.fun_matrix import FUN_ACTIONS
from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    f"funcmd_name fun_{action}_name": case(
        f"funcmd_name fun_{action}_name",
        option_overrides={"user": "__owner__"},
        assert_profile="default",
    )
    for action in FUN_ACTIONS
}
