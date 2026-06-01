from __future__ import annotations

from diagnostics.specs._helpers import register_patch_return, register_patch_targets


def register() -> None:
    register_patch_return("extensions.setup_wizards.api_get_log_channel", 999)
    register_patch_return("extensions.setup_wizards.api_get_level_system_status", True)
    register_patch_targets(
        "setup_wizards.SetupWizardCommands.logs",
        "api_get_log_channel",
    )
    register_patch_targets(
        "setup_wizards.SetupWizardCommands.level",
        "api_get_level_system_status",
    )
    register_patch_targets(
        "setup_wizards.SetupWizardCommands.giveaway",
        "commands.giveaway.start.start_giveaway",
    )
