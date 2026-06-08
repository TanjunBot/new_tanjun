from __future__ import annotations

from tests.helpers.live_e2e.cases._helpers import case

OVERRIDES = {
    "setup_name setup_booster_name": case("setup_name setup_booster_name", assert_profile="games"),
    "setup_name setup_giveaway_name": case("setup_name setup_giveaway_name", assert_profile="games"),
    "setup_name setup_level_name": case("setup_name setup_level_name", assert_profile="games"),
    "setup_name setup_logs_name": case("setup_name setup_logs_name", assert_profile="games"),
}
