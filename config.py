from __future__ import annotations

import sys
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import Field, SecretStr, ValidationError, computed_field
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
    token: SecretStr
    application_id: str = Field(alias="applicationId")
    admin_ids_raw: str = Field(alias="adminIds")
    prefix: str

    # ── Database ──────────────────────────────────────────────────────────────
    database_ip: str
    database_port: int = 3306
    database_password: SecretStr
    database_user: str
    database_schema: str

    # ── External API keys ─────────────────────────────────────────────────────
    giphy_api_key: SecretStr = Field(default=SecretStr(""), alias="giphyAPIKey")
    github_auth_token: SecretStr = Field(default=SecretStr(""), alias="GithubAuthToken")
    imgbb_api_key: SecretStr = Field(default=SecretStr(""), alias="ImgBBApiKey")
    open_ai_key: SecretStr = Field(default=SecretStr(""), alias="openAIKey")
    brawlstars_token: SecretStr = Field(default=SecretStr(""), alias="brawlstarsToken")
    twitch_secret: SecretStr = Field(default=SecretStr(""), alias="twitchSecret")
    twitch_id: str = Field(default="", alias="twitchId")

    # ── Bytebin ───────────────────────────────────────────────────────────────
    bytebin_url: str = ""
    bytebin_password: SecretStr = SecretStr("")
    bytebin_username: str = ""

    # ── OpenRouter ────────────────────────────────────────────────────────────
    openrouter_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="deepseek/deepseek-v4-flash:free", alias="OPENROUTER_MODEL"
    )

    # ── Sentry ─────────────────────────────────────────────────────────────────
    sentry_dsn: str = Field(default="", alias="sentry_dsn")

    # ── Activity ──────────────────────────────────────────────────────────────
    activity: str = "Tanjun {version}"

    # ── Calculator emoji identifiers (loaded from env with sensible defaults) ─
    calc_add: str = Field(default="math_add:1254372629456883793", alias="CALC_ADD")
    calc_subtract: str = Field(default="math_substract:1254372627766837248", alias="CALC_SUBTRACT")
    calc_multiply: str = Field(default="math_multiply:1254372798319558768", alias="CALC_MULTIPLY")
    calc_divide: str = Field(default="math_divide:1254373636224323644", alias="CALC_DIVIDE")
    calc_backspace: str = Field(default="math_backspace:1254371946695757854", alias="CALC_BACKSPACE")

    # ── Welcome emoji (numeric Discord emoji ID) ───────────────────────────────
    welcome_emoji_id_raw: str = Field(default="1266369876524666920", alias="WELCOME_EMOJI_ID")

    # ── Computed properties ───────────────────────────────────────────────────

    @computed_field  # type: ignore[prop-decorator]
    @property
    def admin_ids(self) -> list[int]:
        raw = self.admin_ids_raw
        return [int(x) for x in raw.split(",") if x.strip()] if raw.strip() else []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def welcome_emoji_id(self) -> int | None:
        raw = self.welcome_emoji_id_raw
        return int(raw) if raw.isdigit() else None


try:
    settings = Settings()  # type: ignore[call-arg]
except ValidationError as e:
    print(f"Configuration validation error: {e}", file=sys.stderr)
    sys.exit(1)

# ── Compatibility aliases ─────────────────────────────────────────────────────
# These preserve the original names so that every existing ``from config import
# ...`` keeps working without changes.  Over time, consumers should migrate to
# ``from config import settings`` and use ``settings.<snake_case_name>``.

version = "1.1.4"
token: str = settings.token.get_secret_value()  # type: ignore[assignment]
applicationId: str = settings.application_id  # type: ignore[assignment]
adminIds: list[int] = settings.admin_ids
activity: str = settings.activity
database_ip: str = settings.database_ip  # type: ignore[assignment]
database_port: int = settings.database_port
database_password: str = settings.database_password.get_secret_value()  # type: ignore[assignment]
database_user: str = settings.database_user  # type: ignore[assignment]
database_schema: str = settings.database_schema  # type: ignore[assignment]
giphyAPIKey: str = settings.giphy_api_key.get_secret_value()  # type: ignore[assignment]
GithubAuthToken: str = settings.github_auth_token.get_secret_value()  # type: ignore[assignment]
ImgBBApiKey: str = settings.imgbb_api_key.get_secret_value()  # type: ignore[assignment]
openAiKey: str = settings.open_ai_key.get_secret_value()  # type: ignore[assignment]
bytebin_url: str = settings.bytebin_url  # type: ignore[assignment]
bytebin_password: str = settings.bytebin_password.get_secret_value()  # type: ignore[assignment]
bytebin_username: str = settings.bytebin_username  # type: ignore[assignment]
brawlstarsToken: str = settings.brawlstars_token.get_secret_value()  # type: ignore[assignment]
twitchSecret: str = settings.twitch_secret.get_secret_value()  # type: ignore[assignment]
twitchId: str = settings.twitch_id  # type: ignore[assignment]
prefix: str = settings.prefix  # type: ignore[assignment]
OPENROUTER_API_KEY: str = settings.openrouter_api_key.get_secret_value()
OPENROUTER_MODEL: str = settings.openrouter_model
sentry_dsn: str = settings.sentry_dsn


# ── Emoji identifiers for calculator ─────────────────────────────────────────

CALC_ADD: str = settings.calc_add
CALC_SUBTRACT: str = settings.calc_subtract
CALC_MULTIPLY: str = settings.calc_multiply
CALC_DIVIDE: str = settings.calc_divide
CALC_BACKSPACE: str = settings.calc_backspace

# Emoji ID for welcome command (numeric Discord emoji ID)
WELCOME_EMOJI_ID: int | None = settings.welcome_emoji_id


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
