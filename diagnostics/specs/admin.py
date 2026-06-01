from __future__ import annotations

from diagnostics.specs._helpers import register_defer_and_mock


def register() -> None:
    from diagnostics.assertions import expect_mock_called
    from diagnostics.specs.overrides import SPEC_CUSTOM_ASSERTIONS

    async def _assert_warn_config(_interaction: object, mocks: dict[str, object]) -> None:
        await expect_mock_called("warnConfigCommand", mocks)

    SPEC_CUSTOM_ASSERTIONS["admin.WarnCommands.config"] = _assert_warn_config
    register_defer_and_mock("admin.AdminPurgeCommands.purge", "purgeCommand")
    register_defer_and_mock("admin.AdminChannelCommands.slowmode", "setSlowmodeCommand")
    register_defer_and_mock("admin.AdminChannelCommands.nuke", "nukeChannelCommand")
    register_defer_and_mock("admin.AdminMessagingCommands.say", "sayCommand")
    register_defer_and_mock("admin.AdminMessagingCommands.embed", "createEmbedCommand")
    register_defer_and_mock("admin.AdminSetupCommands.create_ticket", "createTicketCommand")
    register_defer_only("admin.AdminEmojiCommands.createemoji")
