import os

from dotenv import load_dotenv

load_dotenv()

version = "1.0.5"
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

# Emoji identifiers for calculator
CALC_ADD = "math_add:1254372629456883793"
CALC_SUBTRACT = "math_substract:1254372627766837248"
CALC_MULTIPLY = "math_multiply:1254372798319558768"
CALC_DIVIDE = "math_divide:1254373636224323644"
CALC_BACKSPACE = "math_backspace:1254371946695757854"
