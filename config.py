import os
import sys

from dotenv import load_dotenv

load_dotenv()

version = "1.1.4"
token = os.environ.get("token")
applicationId = os.environ.get("applicationId")

admin_ids_str: str | None = os.environ.get("adminIds")
adminIds: list[int] = [int(id) for id in admin_ids_str.split(",")] if admin_ids_str is not None else []

activity = "Tanjun {version}"
database_ip = os.environ.get("database_ip")
database_port = int(os.environ.get("database_port", 3306))
database_password = os.environ.get("database_password")
database_user = os.environ.get("database_user")
database_schema = os.environ.get("database_schema")
giphyAPIKey = os.environ.get("giphyAPIKey")
GithubAuthToken = os.environ.get("GithubAuthToken")
ImgBBApiKey = os.environ.get("ImgBBApiKey")
openAiKey = os.environ.get("openAIKey")
bytebin_url = os.environ.get("bytebin_url")
bytebin_password = os.environ.get("bytebin_password")
bytebin_username = os.environ.get("bytebin_username")
brawlstarsToken = os.environ.get("brawlstarsToken")
twitchSecret = os.environ.get("twitchSecret")
twitchId = os.environ.get("twitchId")
prefix = os.environ.get("prefix")

# ── Required environment variable validation ──────────────────────────────────

REQUIRED_VARS = [
    "token",
    "applicationId",
    "adminIds",
    "database_ip",
    "database_password",
    "database_user",
    "database_schema",
    "prefix",
]

missing = [var for var in REQUIRED_VARS if not os.environ.get(var)]
if missing:
    print(
        f"FATAL: Missing required environment variables: {', '.join(missing)}",
        file=sys.stderr,
    )
    print(
        "Please check your .env file or set these environment variables before starting the bot.",
        file=sys.stderr,
    )
    sys.exit(1)

# Validate numeric env vars

for _port_name, _port_var in (("database_port", database_port),):
    if database_port is not None and not isinstance(database_port, int):
        print(f"FATAL: {_port_name} must be an integer, got {type(database_port).__name__}", file=sys.stderr)
        sys.exit(1)

# Validate boolean/env flag vars (future-proof placeholder)

# Emoji identifiers for calculator
CALC_ADD = "math_add:1254372629456883793"
CALC_SUBTRACT = "math_substract:1254372627766837248"
CALC_MULTIPLY = "math_multiply:1254372798319558768"
CALC_DIVIDE = "math_divide:1254373636224323644"
CALC_BACKSPACE = "math_backspace:1254371946695757854"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash:free")
