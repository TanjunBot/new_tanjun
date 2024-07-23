from discord import Client
import aiohttp
import asyncio

async def ping_server(client: Client):
    print("Sending alive message to server...")
    url = "https://botstatus-api.tanjun.bot"
    payload = {
        "id": str(client.user.id),
        "status": "alive",
        "latency": str(client.latency)
    }
    print(payload)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                print("Sent alive message to server successfully.")
            else:
                print(f"Failed to send message, status code: {response.status}")
