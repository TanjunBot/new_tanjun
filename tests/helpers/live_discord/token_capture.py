from __future__ import annotations

import contextlib
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


def read_user_token_from_auth_state(auth_state_path: str | Path) -> str | None:
    path = Path(auth_state_path)
    if not path.is_file():
        return None
    state = json.loads(path.read_text(encoding="utf-8"))
    for origin in state.get("origins", []):
        if origin.get("origin") != "https://discord.com":
            continue
        for item in origin.get("localStorage", []):
            if item.get("name") != "token":
                continue
            raw = item.get("value")
            if not raw:
                return None
            if isinstance(raw, str) and raw.startswith('"'):
                return json.loads(raw)
            return str(raw)
    return None


def resolve_user_token(
    page: Page,
    *,
    configured_token: str,
    auth_state_path: str | Path,
    timeout_ms: int = 30_000,
    app_gate_timeout_ms: int = 15_000,
) -> str:
    if configured_token.strip():
        return configured_token.strip()
    from_file = read_user_token_from_auth_state(auth_state_path)
    if from_file:
        return from_file.strip()
    return extract_user_token(
        page,
        timeout_ms=timeout_ms,
        app_gate_timeout_ms=app_gate_timeout_ms,
    )


def extract_user_token(
    page: Page,
    *,
    timeout_ms: int = 30_000,
    app_gate_timeout_ms: int = 15_000,
) -> str:
    captured: list[str] = []

    def on_request(request) -> None:
        if "discord.com/api" not in request.url:
            return
        auth = (request.headers.get("authorization") or "").strip()
        if not auth or auth.lower().startswith("bot "):
            return
        captured.append(auth)

    from tests.helpers.live_discord.playwright_ui import ensure_discord_web_client

    page.on("request", on_request)
    page.goto(
        "https://discord.com/channels/@me",
        wait_until="domcontentloaded",
        timeout=timeout_ms,
    )
    ensure_discord_web_client(page, timeout_ms=app_gate_timeout_ms)
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=min(timeout_ms, 15_000))

    deadline = time.monotonic() + (timeout_ms / 1000)
    while time.monotonic() < deadline and not captured:
        page.wait_for_timeout(250)

    if not captured:
        raise RuntimeError(
            f"Could not read user token within {timeout_ms / 1000:.0f}s. "
            "Log in again: python scripts/e2e_discord_login.py"
        )
    return captured[-1]
