PREFIX_COMMANDS_EXCLUDED = frozenset(
    {
        "sendUpdateTextToAllAdmins",
        "sendDemoIsNoMoreToAllAdmins",
        "database_sync",
        "bsstarpoweremojis",
        "bsgadgetsemojis",
        "update",
    }
)

PREFIX_SKIP_REASONS: dict[str, str] = {
    "sendUpdateTextToAllAdmins": "Mass DM to all guild owners",
    "sendDemoIsNoMoreToAllAdmins": "Mass DM to all guild owners",
    "database_sync": "Destructive database import",
    "bsstarpoweremojis": "Creates guild emojis via external API",
    "bsgadgetsemojis": "Creates guild emojis via external API",
    "update": "Triggers bot restart endpoint",
}
