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
database_password = os.environ.get("database_password")
database_user = os.environ.get("database_user")
database_schema = os.environ.get("database_schema")
tenorAPIKey = os.environ.get("tenorAPIKey")
tenorCKey = os.environ.get("tenorCKey")
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
