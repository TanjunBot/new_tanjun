from __future__ import annotations

import sys
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import AliasChoices, Field, SecretStr, ValidationError, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

_VERSION_FILE = Path(__file__).resolve().parent / "VERSION"


def _read_version() -> str:
    if _VERSION_FILE.is_file():
        return _VERSION_FILE.read_text(encoding="utf-8").strip()
    return "0.0.0"


class Settings(BaseSettings, cli_parse_args=False):
    """Application settings loaded from environment variables / .env file.

    All values are validated and typed at startup via pydantic-settings.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    # ── Bot fundamentals ──────────────────────────────────────────────────────
    token: SecretStr
    application_id: str = Field(alias="applicationId")
    admin_ids_raw: str = Field(alias="adminIds")
    prefix: str

    # ── Database ──────────────────────────────────────────────────────────────
    database_ip: str = Field(validation_alias=AliasChoices("database_ip", "MARIADB_HOST", "MYSQL_HOST"))
    database_port: int = Field(
        default=3306,
        validation_alias=AliasChoices("database_port", "MARIADB_PORT", "MYSQL_PORT"),
    )
    database_password: SecretStr = Field(
        validation_alias=AliasChoices("database_password", "MARIADB_PASSWORD", "MYSQL_PASSWORD"),
    )
    database_user: str = Field(validation_alias=AliasChoices("database_user", "MARIADB_USER", "MYSQL_USER"))
    database_schema: str = Field(
        validation_alias=AliasChoices("database_schema", "MARIADB_DATABASE", "MYSQL_DATABASE"),
    )
    database_connect_max_retries: int = Field(default=10, ge=1, le=60)
    database_connect_retry_delay_sec: float = Field(default=3.0, ge=0.5, le=60.0)
    database_connect_timeout_sec: int = Field(default=10, ge=1, le=120)

    # ── External API keys ─────────────────────────────────────────────────────
    giphy_api_key: SecretStr = Field(default=SecretStr(""), alias="giphyAPIKey")
    github_auth_token: SecretStr = Field(default=SecretStr(""), alias="GithubAuthToken")
    imgbb_api_key: SecretStr = Field(default=SecretStr(""), alias="ImgBBApiKey")
    open_ai_key: SecretStr = Field(default=SecretStr(""), alias="openAIKey")
    brawlstars_token: SecretStr = Field(default=SecretStr(""), alias="brawlstarsToken")
    twitch_secret: SecretStr = Field(default=SecretStr(""), alias="twitchSecret")
    twitch_id: str = Field(default="", alias="twitchId")

    # ── OpenRouter (AI chat) ──────────────────────────────────────────────────
    openrouter_api_key: SecretStr = Field(default=SecretStr(""), alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="deepseek/deepseek-v4-flash:free", alias="OPENROUTER_MODEL")

    # ── Bytebin ───────────────────────────────────────────────────────────────
    bytebin_url: str = ""
    bytebin_password: SecretStr = SecretStr("")
    bytebin_username: str = ""

    # ── Sentry ─────────────────────────────────────────────────────────────────
    sentry_dsn: str = Field(default="", alias="sentry_dsn")
    sentry_traces_sample_rate: float = Field(default=0.0, alias="SENTRY_TRACES_SAMPLE_RATE")
    sentry_environment: str = Field(default="", alias="SENTRY_ENVIRONMENT")

    # ── Metrics ───────────────────────────────────────────────────────────────
    metrics_port: int = Field(default=8001, alias="METRICS_PORT")

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

version = _read_version()
token: str = settings.token.get_secret_value()
applicationId: str = settings.application_id
adminIds: list[int] = settings.admin_ids
activity: str = settings.activity
database_ip: str = settings.database_ip
database_port: int = settings.database_port
database_password: str = settings.database_password.get_secret_value()
database_user: str = settings.database_user
database_schema: str = settings.database_schema
database_connect_max_retries: int = settings.database_connect_max_retries
database_connect_retry_delay_sec: float = settings.database_connect_retry_delay_sec
database_connect_timeout_sec: int = settings.database_connect_timeout_sec
giphyAPIKey: str = settings.giphy_api_key.get_secret_value()
GithubAuthToken: str = settings.github_auth_token.get_secret_value()
ImgBBApiKey: str = settings.imgbb_api_key.get_secret_value()
openAiKey: str = settings.open_ai_key.get_secret_value()
bytebin_url: str = settings.bytebin_url
bytebin_password: str = settings.bytebin_password.get_secret_value()
bytebin_username: str = settings.bytebin_username
brawlstarsToken: str = settings.brawlstars_token.get_secret_value()
twitchSecret: str = settings.twitch_secret.get_secret_value()
twitchId: str = settings.twitch_id
prefix: str = settings.prefix
OPENROUTER_API_KEY: str = settings.openrouter_api_key.get_secret_value()
OPENROUTER_MODEL: str = settings.openrouter_model
sentry_dsn: str = settings.sentry_dsn
sentry_traces_sample_rate: float = settings.sentry_traces_sample_rate
sentry_environment: str = settings.sentry_environment
metrics_port: int = settings.metrics_port


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
