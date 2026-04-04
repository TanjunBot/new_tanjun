import aiohttp  # type: ignore[import-not-found]
from discord import Client  # type: ignore[import-not-found]


async def ping_server(client: Client) -> None:  # type: ignore[no-any-unimported]
    if client == None or client.user == None:
        return
    url = "https://botstatus-api.tanjun.bot"
    payload = {"id": str(client.user.id), "status": "alive", "latency": str(client.latency)}

    async with aiohttp.ClientSession() as session, session.post(url, json=payload) as response:
        if response.status != 200:
            print(f"Failed to send message, status code: {response.status}")
