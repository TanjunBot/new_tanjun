import aiohttp

from api import get_twitch_online_notification_by_twitch_uuid
from config import twitchId, twitchSecret
from localizer import tanjunLocalizer
from utility import tanjunEmbed
import discord
from typing import Mapping


class TwitchAPI:
    def __init__(self) -> None:
        self.client_id = twitchId
        self.client_secret = twitchSecret
        self.access_token = None
        self.session: aiohttp.ClientSession | None = None
        self.headers: Mapping[str, str] | None= None
        self.base_url = "https://api.twitch.tv/helix"
        self.stream_status: dict[str, bool] = {}  # Keep track of stream status
        self.initial_check_done = False 

    async def init(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.get_app_access_token()
        await self.setup_headers()

    async def get_app_access_token(self) -> None:
        auth_url = "https://id.twitch.tv/oauth2/token"
        if self.session is None or self.client_id is None or self.client_secret is None:
            return
        
        params: Mapping[str, str] = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
        }

        async with self.session.post(url = auth_url, params = params) as response:
            data = await response.json()
            self.access_token = data["access_token"]

    async def setup_headers(self) -> None:
        if self.client_id is None or self.client_secret is None:
            return
        
        self.headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def get_user_by_login(self, login_name: str) -> dict[str, str] | None:
        if self.session is None:
            return None
        
        url = f"{self.base_url}/users"
        params = {"login": login_name}

        async with self.session.get(url, headers=self.headers, params=params) as response:
            data: dict[str, list[dict[str, str]]] = await response.json()
            if data["data"]:
                return data["data"][0]
            return None

    async def get_streams(self, user_ids: list[str]) -> list[dict[str, str]]:
        if not user_ids or self.session is None:
            return []

        url = f"{self.base_url}/streams"
        params = {"user_id": user_ids}

        async with self.session.get(url, headers=self.headers, params=params) as response:
            data: dict[str, list[dict[str, str]]] = await response.json()
            return data.get("data", [])

    async def initialize_stream_status(self, user_ids: list[str]) -> None:
        if not user_ids:
            return

        streams = await self.get_streams(user_ids)
        for uuid in user_ids:
            self.stream_status[uuid] = any(stream["user_id"] == uuid for stream in streams)
        self.initial_check_done = True


twitch_api = None


async def initTwitch() -> TwitchAPI:
    global twitch_api
    print("initiating Twitch API...")
    twitch_api = TwitchAPI()
    await twitch_api.init()
    print("Twitch API initiated!")
    return twitch_api


def getTwitchApi() -> TwitchAPI | None:
    global twitch_api
    return twitch_api


async def notify_twitch_online(client: discord.Client, uuid: str, data: dict) -> None:
    datas = await get_twitch_online_notification_by_twitch_uuid(uuid)
    if datas is None:
        return
    channelId = datas[1]
    notificationMessage = datas[5]
    guildId = datas[2]
    guild = client.get_guild(int(guildId))
    if guild is None:
        return
    message = parse_twitch_notification_message(
        notificationMessage,
        str(guild.preferred_locale) if guild.preferred_locale else "en",
        data["user_name"],
    )
    channel = guild.get_channel(int(channelId))
    if channel is None or isinstance(channel, discord.ForumChannel) or isinstance(channel, discord.CategoryChannel):
        return
    embed = tanjunEmbed(description=f"[{data['title']}](https://www.twitch.tv/{data['user_name']})")
    embed.set_image(url=data["thumbnail_url"].replace("{width}", "1920").replace("{height}", "1080"))
    await channel.send(message, embed=embed)
    return


async def get_uuid_by_twitch_name(twitch_name: str) -> str | None:
    if not twitch_api:
        return None
    user = await twitch_api.get_user_by_login(twitch_name)
    return user["id"] if user else None


async def subscribe_to_twitch_online_notification(twitch_uuid: str) -> None:
    if not twitch_uuid or not twitch_api:
        return
    # Just add to the status tracking
    twitch_api.stream_status[twitch_uuid] = False


def parse_twitch_notification_message(message: str, locale: str, twitch_name: str) -> str:
    if not message:
        return tanjunLocalizer.localize(locale, "commands.utility.twitch.defaultNotificationMessage").replace(
            "{name}", twitch_name
        )
    return message.replace("{name}", twitch_name)
