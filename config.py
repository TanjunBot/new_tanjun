import os
from dotenv import load_dotenv

load_dotenv()

version = "0.4.5"
token = os.getenv("token")
applicationId = "832297321793323028"
adminIds = [766350321638309958, 471036610561966111]
activity = "Tanjun {version}"
database_ip = os.getenv("database_ip")
database_password = os.getenv("database_password")
database_user = os.getenv("database_user")
database_schema = "tanjun"
tenorAPIKey = os.getenv("tenorAPIKey")
tenorCKey = os.getenv("tenorCKey")
GithubAuthToken = os.getenv("GithubAuthToken")
ImgBBApiKey = os.getenv("ImgBBApiKey")
