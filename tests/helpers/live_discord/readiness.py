from __future__ import annotations

import os
from pathlib import Path

from tests.helpers.live_discord.config import ROOT, _ensure_dotenv_loaded, load_live_e2e_config


def live_e2e_skip_reason() -> str | None:
    _ensure_dotenv_loaded()
    missing: list[str] = []

    bot_token = (
        os.getenv("TANJUN_TEST_BOT_TOKEN", "").strip()
        or os.getenv("token", "").strip()
    )
    if not bot_token:
        missing.append("TANJUN_TEST_BOT_TOKEN (or token in .env)")

    application_id = (
        os.getenv("TANJUN_TEST_APPLICATION_ID", "").strip()
        or os.getenv("applicationId", "").strip()
    )
    if not application_id:
        missing.append("TANJUN_TEST_APPLICATION_ID (or applicationId in .env)")

    bot_user_id = (
        os.getenv("TANJUN_E2E_BOT_USER_ID", "").strip()
        or os.getenv("DOC_SCREENSHOT_BOT_USER_ID", "").strip()
        or application_id
    )
    if not bot_user_id:
        missing.append("TANJUN_E2E_BOT_USER_ID")

    auth_raw = os.getenv(
        "TANJUN_E2E_AUTH_STATE",
        os.getenv("DOC_SCREENSHOT_AUTH_STATE", ".discord-doc-auth.json"),
    ).strip()
    auth_path = Path(auth_raw) if Path(auth_raw).is_absolute() else ROOT / auth_raw
    if not auth_path.is_file():
        missing.append(f"Playwright session file ({auth_path}) — run: python scripts/e2e_discord_login.py")

    if missing:
        return "Live E2E not configured: " + "; ".join(missing)

    try:
        load_live_e2e_config()
    except RuntimeError as exc:
        return str(exc)

    return None
