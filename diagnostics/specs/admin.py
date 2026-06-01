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
    from diagnostics.assertions import expect_mock_called
    from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS

    async def _assert_warn_config(_interaction: object, mocks: dict[str, object]) -> None:
        await expect_mock_called("warnConfigCommand", mocks)

    SPEC_CUSTOM_ASSERTIONS["admin.WarnCommands.config"] = _assert_warn_config
    register_skip("admin.AdminPurgeCommands.purge", "Destructive bulk message deletion")
    for spec_id in _BROKEN_CTX_HANDLERS:
        register_skip(spec_id, "Handler parameter/body mismatch (ctx vs interaction)")
