from __future__ import annotations

from typing import Any

SPEC_SKIPS: dict[str, str] = {}

SPEC_OVERRIDES: dict[str, dict[str, Any] | Any] = {}

SPEC_PATCH_TARGETS: dict[str, tuple[str, ...]] = {}

SPEC_PATCH_EXCLUDE: dict[str, tuple[str, ...]] = {}

SPEC_CUSTOM_ASSERTIONS: dict[str, Any] = {}

SPEC_COMMAND_HANDLERS: dict[str, str] = {
    "ai_name ai_askcustom_name": "tests.helpers.command_matrix.manual_handlers.ask_custom_situation",
    "setup_name setup_logs_name": "tests.helpers.command_matrix.manual_handlers.setup_logs_wizard",
    "setup_name setup_level_name": "tests.helpers.command_matrix.manual_handlers.setup_level_wizard",
    "setup_name setup_giveaway_name": "tests.helpers.command_matrix.manual_handlers.setup_giveaway_wizard",
    "setup_name setup_booster_name": "tests.helpers.command_matrix.manual_handlers.setup_booster_wizard",
    "utilitycmd_name utility_boosterchannel_name utility_boosterchannelinfo_name": "tests.helpers.command_matrix.manual_handlers.booster_channel_info",
    "utilitycmd_name utility_boosterrole_name utility_boosterroleinfo_name": "tests.helpers.command_matrix.manual_handlers.booster_role_info",
    "utilitycmd_name utility_feedback_name": "tests.helpers.command_matrix.manual_handlers.feedback_command",
}
