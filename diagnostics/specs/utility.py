from __future__ import annotations

from diagnostics.assertions import expect_interaction_or_modal
from diagnostics.specs._helpers import default_channel_kwargs, default_role_kwargs, register_kwargs
from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS


def register() -> None:
    register_kwargs("utility.MessageTrackingCommands.setmessagechannel", default_channel_kwargs)
    register_kwargs("utility.BoosterRoleCommands.setupboosterrole", default_role_kwargs)
    register_kwargs("utility.BoosterChannelCommands.setboosterchannel", default_channel_kwargs)
    SPEC_CUSTOM_ASSERTIONS["utility.UtilityCommands.feedback"] = expect_interaction_or_modal
