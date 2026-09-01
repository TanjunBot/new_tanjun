from __future__ import annotations

import json
import re
from typing import Any


class DiscordRateLimitedError(RuntimeError):
    def __init__(self, message: str, *, retry_after_sec: float | None = None) -> None:
        super().__init__(message)
        self.retry_after_sec = retry_after_sec


def retry_after_from_headers(headers: Any) -> float | None:
    if headers is None:
        return None
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def retry_after_from_payload(payload: str) -> float | None:
    if not payload:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        for key in ("retry_after", "retry_after_ms"):
            if key in data:
                value = data[key]
                if key == "retry_after_ms":
                    return float(value) / 1000.0
                return float(value)
    match = re.search(r'"retry_after"\s*:\s*([0-9.]+)', payload)
    if match:
        return float(match.group(1))
    return None


def is_rate_limited_status(status: int, payload: str = "") -> bool:
    if status == 429:
        return True
    lowered = payload.lower()
    return "rate limit" in lowered or "rate_limited" in lowered


def raise_for_rate_limit(
    *,
    status: int,
    payload: str,
    headers: Any = None,
    action: str,
) -> None:
    if not is_rate_limited_status(status, payload):
        return
    retry_after = retry_after_from_headers(headers) or retry_after_from_payload(payload)
    wait_hint = (
        f" Wait {retry_after:.0f}s and retry."
        if retry_after is not None
        else " Wait 30–60 minutes before retrying live E2E."
    )
    reuse_hint = (
        " To avoid guild/OAuth churn, set TANJUN_E2E_GUILD_ID and TANJUN_E2E_CHANNEL_ID "
        "to a permanent test server where the bot is already invited."
    )
    raise DiscordRateLimitedError(
        f"Discord rate limited during {action} ({status}): {payload[:300]}.{wait_hint}{reuse_hint}",
        retry_after_sec=retry_after,
    )


def is_captcha_payload(payload: str) -> bool:
    return "captcha" in payload.lower()
