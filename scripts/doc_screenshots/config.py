from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class AuthSessionConfig:
    auth_state_path: Path


@dataclass(frozen=True)
class DocScreenshotConfig:
    guild_id: str
    channel_id: str
    bot_user_id: str
    auth_state_path: Path
    headless: bool
    default_wait_ms: int
    viewport_width: int
    viewport_height: int
    manifest_path: Path


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def resolve_auth_state_path() -> Path:
    load_dotenv(ROOT / ".env")
    auth_raw = os.getenv(
        "TANJUN_E2E_AUTH_STATE",
        os.getenv("DOC_SCREENSHOT_AUTH_STATE", ".discord-doc-auth.json"),
    ).strip()
    if Path(auth_raw).is_absolute():
        return Path(auth_raw)
    return (ROOT / auth_raw).resolve()


def load_login_config() -> AuthSessionConfig:
    return AuthSessionConfig(auth_state_path=resolve_auth_state_path())


def load_config() -> DocScreenshotConfig:
    load_dotenv(ROOT / ".env")

    guild_id = os.getenv("DOC_SCREENSHOT_GUILD_ID", "").strip()
    channel_id = os.getenv("DOC_SCREENSHOT_CHANNEL_ID", "").strip()
    bot_user_id = os.getenv("DOC_SCREENSHOT_BOT_USER_ID", "").strip()

    missing = [
        name
        for name, value in (
            ("DOC_SCREENSHOT_GUILD_ID", guild_id),
            ("DOC_SCREENSHOT_CHANNEL_ID", channel_id),
            ("DOC_SCREENSHOT_BOT_USER_ID", bot_user_id),
        )
        if not value
    ]
    if missing:
        msg = ", ".join(missing)
        raise SystemExit(
            f"Missing required env vars: {msg}. "
            "See .env.example and docs/dev/doc_screenshots.md."
        )

    manifest_raw = os.getenv(
        "DOC_SCREENSHOT_MANIFEST",
        str(ROOT / "docs" / "screenshots.manifest.yaml"),
    ).strip()

    return DocScreenshotConfig(
        guild_id=guild_id,
        channel_id=channel_id,
        bot_user_id=bot_user_id,
        auth_state_path=resolve_auth_state_path(),
        headless=_env_bool("DOC_SCREENSHOT_HEADLESS", True),
        default_wait_ms=int(os.getenv("DOC_SCREENSHOT_WAIT_MS", "4000")),
        viewport_width=int(os.getenv("DOC_SCREENSHOT_VIEWPORT_WIDTH", "1280")),
        viewport_height=int(os.getenv("DOC_SCREENSHOT_VIEWPORT_HEIGHT", "720")),
        manifest_path=(ROOT / manifest_raw).resolve()
        if not Path(manifest_raw).is_absolute()
        else Path(manifest_raw),
    )
