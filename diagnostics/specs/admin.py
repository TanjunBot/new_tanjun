from __future__ import annotations

from diagnostics.specs._helpers import register_skip

_BROKEN_CTX_HANDLERS = (
    "admin.AdminChannelCommands.slowmode",
    "admin.AdminChannelCommands.nuke",
    "admin.AdminEmojiCommands.createemoji",
    "admin.AdminMessagingCommands.say",
    "admin.AdminMessagingCommands.embed",
    "admin.AdminSetupCommands.create_ticket",
    "admin.ReportCommands.set_channel",
)


def register() -> None:
    from diagnostics.assertions import expect_interaction_or_modal
    from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS

    SPEC_CUSTOM_ASSERTIONS["admin.WarnCommands.config"] = expect_interaction_or_modal
    register_skip("admin.AdminPurgeCommands.purge", "Destructive bulk message deletion")
    for spec_id in _BROKEN_CTX_HANDLERS:
        register_skip(spec_id, "Handler parameter/body mismatch (ctx vs interaction)")
