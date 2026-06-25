from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    "ai_name ai_askcustom_name": case(
        "ai_name ai_askcustom_name",
        option_overrides={"situation": "e2e test", "prompt": "hello"},
        assert_profile="ai",
    ),
    "ai_name ai_askgpt_name": case(
        "ai_name ai_askgpt_name",
        option_overrides={"prompt": "Say hi in one word"},
        assert_profile="ai",
    ),
    "ai_name ai_asktanjuwun_name": case(
        "ai_name ai_asktanjuwun_name",
        option_overrides={"prompt": "hello"},
        assert_profile="ai",
    ),
    "ai_name ai_customsituations_name ai_createcustom_name": case(
        "ai_name ai_customsituations_name ai_createcustom_name",
        option_overrides={"situation": "e2e custom"},
        teardown="ai.delete_custom",
    ),
    "ai_name ai_customsituations_name ai_deletecustom_name": case(
        "ai_name ai_customsituations_name ai_deletecustom_name",
        setup="ai.create_custom",
    ),
    "ai_name ai_tokens_name": case("ai_name ai_tokens_name", assert_profile="ai"),
}
