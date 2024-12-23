import aiohttp
import asyncio
from config import twitchSecret, twitchId
from api import get_twitch_online_notification_by_twitch_uuid, get_all_twitch_notification_uuids
from localizer import tanjunLocalizer
from utility import tanjunEmbed

class TwitchAPI:
    def __init__(self):
        self.client_id = twitchId
        self.client_secret = twitchSecret
        self.access_token = None
        self.session = None
        self.headers = None
        self.base_url = "https://api.twitch.tv/helix"
        self.stream_status = {}  # Keep track of stream status
        self.initial_check_done = False  # Add this line

    async def init(self):
        self.session = aiohttp.ClientSession()
        await self.get_app_access_token()
        await self.setup_headers()
        return self

    async def cleanup(self):
        if self.session:
            await self.session.close()

    async def get_app_access_token(self):
        auth_url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        async with self.session.post(auth_url, params=params) as response:
            data = await response.json()
            self.access_token = data["access_token"]

    async def setup_headers(self):
        self.headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get_user_by_login(self, login_name: str):
        url = f"{self.base_url}/users"
        params = {"login": login_name}
        
        async with self.session.get(url, headers=self.headers, params=params) as response:
            data = await response.json()
            if data["data"]:
                return data["data"][0]
            return None

    async def get_streams(self, user_ids: list[str]):
        if not user_ids:
            return []
        
        url = f"{self.base_url}/streams"
        params = {"user_id": user_ids}
        
        async with self.session.get(url, headers=self.headers, params=params) as response:
            data = await response.json()
            return data.get("data", [])

    async def initialize_stream_status(self, user_ids: list[str]):
        if not user_ids:
            return
            
        streams = await self.get_streams(user_ids)
        # Initialize status for all tracked streamers
        for uuid in user_ids:
            self.stream_status[uuid] = any(stream["user_id"] == uuid for stream in streams)
        self.initial_check_done = True

# Global instance
twitch_api = None

async def initTwitch():
    global twitch_api
    print("initiating Twitch API...")
    twitch_api = TwitchAPI()
    await twitch_api.init()
    print("Twitch API initiated!")
    return twitch_api

def getTwitchApi():
    global twitch_api
    return twitch_api

async def notify_twitch_online(client, uuid, data: dict):
    print("notifying twitch online: ", uuid, data)
    datas = await get_twitch_online_notification_by_twitch_uuid(uuid)
    channelId = datas[1]
    notificationMessage = datas[5]
    guildId = datas[2]
    guild = client.get_guild(int(guildId))
    message = parse_twitch_notification_message(notificationMessage, guild.preferred_locale if guild.preferred_locale else "en", data["user_name"])
    channel = guild.get_channel(int(channelId))
    if not channel:
        print("channel not found :(")
        return
    embed = tanjunEmbed(
        description=f"[{data['title']}](https://www.twitch.tv/{data['user_name']})"
    )
    embed.set_image(url = data["thumbnail_url"].replace("{width}", "1920").replace("{height}", "1080"))
    await channel.send(message, embed=embed)
    return

async def get_uuid_by_twitch_name(twitch_name: str):
    if not twitch_api:
        return None
    user = await twitch_api.get_user_by_login(twitch_name)
    return user["id"] if user else None

async def subscribe_to_twitch_online_notification(twitch_uuid: str):
    if not twitch_uuid or not twitch_api:
        return
    # Just add to the status tracking
    twitch_api.stream_status[twitch_uuid] = False

def parse_twitch_notification_message(message: str, locale: str, twitch_name: str):
    if not message:
        return tanjunLocalizer.localize(locale, "commands.utility.twitch.defaultNotificationMessage").replace("{name}", twitch_name)
    return message.replace("{name}", twitch_name)