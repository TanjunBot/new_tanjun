from __future__ import annotations

import os
import sys
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings, cli_parse_args=False):
    """Application settings loaded from environment variables / .env file.

    All values are validated and typed at startup via pydantic-settings.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Bot fundamentals ──────────────────────────────────────────────────────
    token: str
    application_id: str = Field(alias="applicationId")
    admin_ids_raw: str = Field(default="", alias="adminIds")
    prefix: str

    # ── Database ──────────────────────────────────────────────────────────────
    database_ip: str
    database_port: int = 3306
    database_password: str
    database_user: str
    database_schema: str

    # ── External API keys ─────────────────────────────────────────────────────
    giphy_api_key: str = Field(default="", alias="giphyAPIKey")
    github_auth_token: str = Field(default="", alias="GithubAuthToken")
    imgbb_api_key: str = Field(default="", alias="ImgBBApiKey")
    open_ai_key: str = Field(default="", alias="openAIKey")
    brawlstars_token: str = Field(default="", alias="brawlstarsToken")
    twitch_secret: str = Field(default="", alias="twitchSecret")
    twitch_id: str = Field(default="", alias="twitchId")

    # ── Bytebin ───────────────────────────────────────────────────────────────
    bytebin_url: str = ""
    bytebin_password: str = ""
    bytebin_username: str = ""

    # ── OpenRouter ────────────────────────────────────────────────────────────
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="deepseek/deepseek-v4-flash:free", alias="OPENROUTER_MODEL"
    )

    # ── Activity ──────────────────────────────────────────────────────────────
    activity: str = "Tanjun {version}"

    # ── Computed properties ───────────────────────────────────────────────────

    @computed_field  # type: ignore[prop-decorator]
    @property
    def admin_ids(self) -> list[int]:
        raw = self.admin_ids_raw
        return [int(x) for x in raw.split(",") if x.strip()] if raw.strip() else []


settings = Settings()

# ── Compatibility aliases ─────────────────────────────────────────────────────
# These preserve the original names so that every existing ``from config import
# ...`` keeps working without changes.  Over time, consumers should migrate to
# ``from config import settings`` and use ``settings.<snake_case_name>``.

version = "1.1.4"
token: str = settings.token  # type: ignore[assignment]
applicationId: str = settings.application_id  # type: ignore[assignment]
adminIds: list[int] = settings.admin_ids
activity: str = settings.activity
database_ip: str = settings.database_ip  # type: ignore[assignment]
database_port: int = settings.database_port
database_password: str = settings.database_password  # type: ignore[assignment]
database_user: str = settings.database_user  # type: ignore[assignment]
database_schema: str = settings.database_schema  # type: ignore[assignment]
giphyAPIKey: str = settings.giphy_api_key  # type: ignore[assignment]
GithubAuthToken: str = settings.github_auth_token  # type: ignore[assignment]
ImgBBApiKey: str = settings.imgbb_api_key  # type: ignore[assignment]
openAiKey: str = settings.open_ai_key  # type: ignore[assignment]
bytebin_url: str = settings.bytebin_url  # type: ignore[assignment]
bytebin_password: str = settings.bytebin_password  # type: ignore[assignment]
bytebin_username: str = settings.bytebin_username  # type: ignore[assignment]
brawlstarsToken: str = settings.brawlstars_token  # type: ignore[assignment]
twitchSecret: str = settings.twitch_secret  # type: ignore[assignment]
twitchId: str = settings.twitch_id  # type: ignore[assignment]
prefix: str = settings.prefix  # type: ignore[assignment]
OPENROUTER_API_KEY: str = settings.openrouter_api_key
OPENROUTER_MODEL: str = settings.openrouter_model


# ── Emoji identifiers for calculator ─────────────────────────────────────────

CALC_ADD = "math_add:1254372629456883793"
CALC_SUBTRACT = "math_substract:1254372627766837248"
CALC_MULTIPLY = "math_multiply:1254372798319558768"
CALC_DIVIDE = "math_divide:1254373636224323644"
CALC_BACKSPACE = "math_backspace:1254371946695757854"


# ── Startup validation ───────────────────────────────────────────────────────
# pydantic-settings already validates types, but we keep a fast-path check for
# the minimum required vars so the bot fails immediately on missing config.

_REQUIRED_ATTRS: tuple[str, ...] = (
    "token",
    "application_id",
    "database_ip",
    "database_password",
    "database_user",
    "database_schema",
    "prefix",
)

_missing = [name for name in _REQUIRED_ATTRS if not getattr(settings, name, None)]
if _missing:
    print(
        f"FATAL: Missing required setting(s): {', '.join(_missing)}",
        file=sys.stderr,
    )
    print(
        "Please check your .env file or set these environment variables.",
        file=sys.stderr,
    )
    sys.exit(1)
