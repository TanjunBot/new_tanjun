from __future__ import annotations

from diagnostics.specs._helpers import register_skip


def register() -> None:
    register_skip("setup_wizards.SetupWizardCommands.level", "Interactive wizard blocks on view.wait()")
    register_skip("setup_wizards.SetupWizardCommands.giveaway", "Launches full giveaway builder UI")
    register_skip("setup_wizards.SetupWizardCommands.logs", "Interactive channel-select view")
    register_skip("setup_wizards.SetupWizardCommands.booster", "Interactive booster setup view")
