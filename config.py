import os
from dotenv import load_dotenv

load_dotenv()

version = "0.4.8"
token = config["token"]
applicationId = "832297321793323028"
adminIds = [766350321638309958, 471036610561966111]
activity = "Tanjun {version}"
database_ip = config["database_ip"]
database_password = config["database_password"]
database_user = config["database_user"]
database_schema = "testTanjun"
tenorAPIKey = config["tenorAPIKey"]
tenorCKey = config["tenorCKey"]
GithubAuthToken = config["GithubAuthToken"]
ImgBBApiKey = config["ImgBBApiKey"]
