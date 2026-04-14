# Unused imports:
# import os

from dotenv import dotenv_values

config: dict[str, str | None] = dotenv_values(".env")

version = "1.0.5"
token = config["token"]
applicationId = config["applicationId"]
admin_ids_str: str | None = config.get("adminIds")
adminIds: list[int] = [int(id) for id in admin_ids_str.split(",")] if admin_ids_str is not None else []
activity = "Tanjun {version}"
database_ip = config["database_ip"]
database_password = config["database_password"]
database_user = config["database_user"]
database_schema = config["database_schema"]
tenorAPIKey = config["tenorAPIKey"]
tenorCKey = config["tenorCKey"]
GithubAuthToken = config["GithubAuthToken"]
ImgBBApiKey = config["ImgBBApiKey"]
openAiKey = config["openAIKey"]
bytebin_url = config["bytebin_url"]
bytebin_password = config["bytebin_password"]
bytebin_username = config["bytebin_username"]
brawlstarsToken = config["brawlstarsToken"]
twitchSecret = config["twitchSecret"]
twitchId = config["twitchId"]
prefix = config["prefix"]
