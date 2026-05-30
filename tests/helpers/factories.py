from __future__ import annotations

from datetime import datetime, timezone

GUILD_ID = "12345678901234567"
USER_ID = "11111111111111111"
CHANNEL_ID = "44444444444444444"
ROLE_ID = "77777777777777777"
MESSAGE_ID = "99999999999999999"


def _dt() -> datetime:
    return datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


def giveaway_row(**overrides):
    base = (
        1,
        GUILD_ID,
        "Test Giveaway",
        "Description",
        1,
        True,
        "custom",
        "sponsor",
        "10€",
        "msg",
        _dt(),
        _dt(),
        True,
        False,
        0,
        0,
        0,
        False,
        CHANNEL_ID,
        "55555555555555555",
        _dt(),
    )
    if not overrides:
        return base
    data = list(base)
    for idx, val in overrides.items():
        data[idx] = val
    return tuple(data)


def warning_row(**overrides):
    base = (1, GUILD_ID, USER_ID, "Test reason", _dt(), None, "22222222222222222", 0)
    if not overrides:
        return base
    data = list(base)
    for idx, val in overrides.items():
        data[idx] = val
    return tuple(data)


def xp_boost_row(boost: float = 2.0, additive: bool = False):
    return (boost, additive)


def level_role_row(level: int = 5, role_id: str = ROLE_ID):
    return (level, role_id)


def guild_config_row(guild_id: str = GUILD_ID, locale: str = "en-US"):
    return (guild_id, locale)


def twitch_notification_row(
    guild_id: str = GUILD_ID,
    channel_id: str = CHANNEL_ID,
    twitch_username: str = "teststreamer",
):
    return (guild_id, channel_id, twitch_username, _dt())


def afk_row(user_id: str = USER_ID, reason: str = "sleeping"):
    return (user_id, reason, _dt())
