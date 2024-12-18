import os
from dotenv import dotenv_values

config = dotenv_values(".env")

version = "0.7.13"
token = config["token"]
applicationId = config["applicationId"]
adminIds = list(config["adminIds"])
activity = "Tanjun {version}"
database_ip = config["database_ip"]
database_password = config["database_password"]
database_user = config["database_user"]
database_schema = "testTanjun"
tenorAPIKey = config["tenorAPIKey"]
tenorCKey = config["tenorCKey"]
GithubAuthToken = config["GithubAuthToken"]
ImgBBApiKey = config["ImgBBApiKey"]
openAiKey = config["openAIKey"]
bytebin_url = config["bytebin_url"]
bytebin_password = config["bytebin_password"]
bytebin_username = config["bytebin_username"]

