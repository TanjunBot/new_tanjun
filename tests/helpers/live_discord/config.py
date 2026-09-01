from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

from tests.helpers.live_discord.timeouts import LiveE2ETimeouts

ROOT = Path(__file__).resolve().parents[3]

BootstrapMode = Literal["auto", "api_only", "playwright"]


def _ensure_dotenv_loaded() -> None:
    load_dotenv(ROOT / ".env")
    test_env = ROOT / ".env.test"
    if test_env.is_file():
        load_dotenv(test_env, override=False)


@dataclass(frozen=True)
class LiveE2EConfig:
    user_token: str
    bot_token: str
    application_id: str
    bot_user_id: str
    auth_state_path: Path
    headless: bool
    command_wait_ms: int
    command_sync_timeout_sec: int
    guild_name_prefix: str
    reuse_guild_id: str | None
    reuse_channel_id: str | None
    secondary_user_id: str | None
    disposable_channel_id: str | None
    oauth_headless: bool
    bot_invite_permissions: str
    fun_group_name: str
    required_command_roots: tuple[str, ...]
    skip_command_sync: bool
    case_filter: str | None
    debug_screenshots_dir: Path | None
    user_display_name: str
    timeouts: LiveE2ETimeouts
    bootstrap_mode: BootstrapMode
    interaction_api_version: str
    command_interval_ms: int
    command_retry_count: int


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _default_oauth_headless() -> bool:
    raw = os.getenv("TANJUN_E2E_OAUTH_HEADLESS")
    if raw is not None:
        return _env_bool("TANJUN_E2E_OAUTH_HEADLESS", True)
    return not bool(os.getenv("DISPLAY", "").strip())


def load_live_e2e_config() -> LiveE2EConfig:
    _ensure_dotenv_loaded()

    user_token = os.getenv("TANJUN_E2E_USER_TOKEN", "").strip()
    bot_token = (
        os.getenv("TANJUN_TEST_BOT_TOKEN", "").strip()
        or os.getenv("token", "").strip()
        or os.getenv("TOKEN", "").strip()
    )
    application_id = (
        os.getenv("TANJUN_TEST_APPLICATION_ID", "").strip()
        or os.getenv("applicationId", "").strip()
        or os.getenv("APPLICATION_ID", "").strip()
    )
    bot_user_id = (
        os.getenv("TANJUN_E2E_BOT_USER_ID", "").strip()
        or os.getenv("DOC_SCREENSHOT_BOT_USER_ID", "").strip()
        or application_id
    )

    missing = [
        name
        for name, value in (
            ("TANJUN_TEST_BOT_TOKEN", bot_token),
            ("TANJUN_TEST_APPLICATION_ID", application_id),
            ("TANJUN_E2E_BOT_USER_ID or DOC_SCREENSHOT_BOT_USER_ID", bot_user_id),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(f"Missing live E2E env: {', '.join(missing)}")

    auth_raw = os.getenv(
        "TANJUN_E2E_AUTH_STATE",
        os.getenv("DOC_SCREENSHOT_AUTH_STATE", ".discord-doc-auth.json"),
    ).strip()
    auth_path = (ROOT / auth_raw).resolve() if not Path(auth_raw).is_absolute() else Path(auth_raw)

    debug_dir: Path | None = None
    if _env_bool("TANJUN_E2E_DEBUG_SCREENSHOTS", False):
        debug_dir = (ROOT / "tests" / "e2e_live" / "_debug_screenshots").resolve()
        debug_dir.mkdir(parents=True, exist_ok=True)

    timeouts = LiveE2ETimeouts.from_env(
        playwright_default_ms=int(os.getenv("TANJUN_E2E_PLAYWRIGHT_TIMEOUT_MS", "30000")),
        playwright_navigation_ms=int(os.getenv("TANJUN_E2E_NAVIGATION_TIMEOUT_MS", "60000")),
        bootstrap_sec=float(os.getenv("TANJUN_E2E_BOOTSTRAP_TIMEOUT_SEC", "180")),
        token_capture_ms=int(os.getenv("TANJUN_E2E_TOKEN_CAPTURE_TIMEOUT_MS", "30000")),
        app_gate_ms=int(os.getenv("TANJUN_E2E_APP_GATE_TIMEOUT_MS", "15000")),
        guild_create_ms=int(os.getenv("TANJUN_E2E_GUILD_CREATE_TIMEOUT_MS", "90000")),
        oauth_ui_ms=int(os.getenv("TANJUN_E2E_OAUTH_TIMEOUT_MS", "25000")),
        oauth_scroll_ms=int(os.getenv("TANJUN_E2E_OAUTH_SCROLL_TIMEOUT_MS", "60000")),
        open_channel_ms=int(os.getenv("TANJUN_E2E_OPEN_CHANNEL_TIMEOUT_MS", "45000")),
    )

    reuse_guild = (
        os.getenv("TANJUN_E2E_GUILD_ID", "").strip()
        or os.getenv("DOC_SCREENSHOT_GUILD_ID", "").strip()
    )
    reuse_channel = (
        os.getenv("TANJUN_E2E_CHANNEL_ID", "").strip()
        or os.getenv("DOC_SCREENSHOT_CHANNEL_ID", "").strip()
    )
    if reuse_guild and not reuse_channel:
        from tests.helpers.live_discord.discord_api_sync import default_text_channel_id_for_guild

        reuse_channel = default_text_channel_id_for_guild(bot_token, reuse_guild)
    if reuse_channel and not reuse_guild:
        raise RuntimeError(
            "TANJUN_E2E_CHANNEL_ID is set without TANJUN_E2E_GUILD_ID. "
            "Set the guild id of your permanent test server."
        )

    from diagnostics.tree import load_manifest
    from tests.helpers.fun_matrix import resolve_fun_group_name

    manifest_roots = tuple(load_manifest().get("roots") or [])
    roots_raw = os.getenv("TANJUN_E2E_REQUIRED_COMMAND_ROOTS", "").strip()
    if roots_raw:
        required_command_roots = tuple(
            part.strip() for part in roots_raw.split(",") if part.strip()
        )
    else:
        required_command_roots = manifest_roots

    secondary_user_id = os.getenv("TANJUN_E2E_SECONDARY_USER_ID", "").strip() or None
    disposable_channel_id = (
        os.getenv("TANJUN_E2E_DISPOSABLE_CHANNEL_ID", "").strip() or None
    )
    case_filter = os.getenv("TANJUN_E2E_CASE_FILTER", "").strip() or None

    skip_command_sync_raw = os.getenv("TANJUN_E2E_SKIP_COMMAND_SYNC")
    if skip_command_sync_raw is None:
        skip_command_sync = bool(reuse_guild)
    else:
        skip_command_sync = skip_command_sync_raw.strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    bootstrap_raw = os.getenv("TANJUN_E2E_BOOTSTRAP_MODE", "auto").strip().lower()
    if bootstrap_raw not in {"auto", "api_only", "playwright"}:
        raise RuntimeError(
            f"Invalid TANJUN_E2E_BOOTSTRAP_MODE={bootstrap_raw!r}. "
            "Use auto, api_only, or playwright."
        )

    return LiveE2EConfig(
        user_token=user_token,
        bot_token=bot_token,
        application_id=application_id,
        bot_user_id=bot_user_id,
        auth_state_path=auth_path,
        headless=_env_bool("TANJUN_E2E_HEADLESS", True),
        command_wait_ms=int(os.getenv("TANJUN_E2E_COMMAND_WAIT_MS", "15000")),
        command_sync_timeout_sec=int(os.getenv("TANJUN_E2E_COMMAND_SYNC_TIMEOUT_SEC", "180")),
        guild_name_prefix=os.getenv("TANJUN_E2E_GUILD_NAME_PREFIX", "tanjun-e2e"),
        reuse_guild_id=reuse_guild or None,
        reuse_channel_id=reuse_channel or None,
        secondary_user_id=secondary_user_id,
        disposable_channel_id=disposable_channel_id,
        oauth_headless=_default_oauth_headless(),
        bot_invite_permissions=os.getenv("TANJUN_E2E_BOT_PERMISSIONS", "84992").strip(),
        fun_group_name=resolve_fun_group_name(),
        required_command_roots=required_command_roots,
        skip_command_sync=skip_command_sync,
        case_filter=case_filter,
        debug_screenshots_dir=debug_dir,
        user_display_name=os.getenv("TANJUN_E2E_USER_DISPLAY_NAME", "").strip(),
        timeouts=timeouts,
        bootstrap_mode=bootstrap_raw,
        interaction_api_version=os.getenv("TANJUN_E2E_INTERACTION_API_VERSION", "v10").strip(),
        command_interval_ms=int(os.getenv("TANJUN_E2E_COMMAND_INTERVAL_MS", "500")),
        command_retry_count=int(os.getenv("TANJUN_E2E_COMMAND_RETRY_COUNT", "2")),
    )
