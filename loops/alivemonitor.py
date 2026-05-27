import aiohttp
from aiohttp import ClientTimeout
from discord import Client


async def ping_server(client: Client) -> None:
    if client == None or client.user == None:
        return
    url = "https://botstatus-api.tanjun.bot"
    payload = {"id": str(client.user.id), "status": "alive", "latency": str(client.latency)}

    async with (
        aiohttp.ClientSession() as session,
        session.post(url, json=payload, timeout=ClientTimeout(total=10)) as response,
    ):
        if response.status != 200:
            print(f"Failed to send message, status code: {response.status}")
