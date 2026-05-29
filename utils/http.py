"""HTTP-related utilities: GIF search, ImgBB upload, bytebin log upload.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

import gzip
import random

import aiohttp
from aiohttp import ClientTimeout

from config import (
    ImgBBApiKey,
    bytebin_password,
    bytebin_url,
    bytebin_username,
    giphyAPIKey,
)


async def getGif(query: str, amount: int = 1, limit: int = 10) -> list[str]:
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:

            async def fetch(url: str) -> dict | None:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    return await response.json()

            r = await fetch(
                f"https://api.giphy.com/v1/gifs/search?api_key={giphyAPIKey}&q={query}&limit={limit}&rating=pg"
            )

            if r is None:
                return []
            results = r.get("data", [])
            # nosec: B311
            random.shuffle(results)

            return [results[i]["images"]["downsized_medium"]["url"] for i in range(min(amount, len(results)))]
    except (TimeoutError, aiohttp.ClientError):
        return []


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> dict:
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        form_data = aiohttp.FormData()
        form_data.add_field("key", ImgBBApiKey)
        form_data.add_field("image", image_bytes, filename=f"upload.{file_extension}")
        form_data.add_field("name", "tbg")

        async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
            response_data = await response.json()

    return response_data


async def upload_to_tanjun_logs(content: str) -> str:
    compressed_content = gzip.compress(content.encode("utf-8"))
    url = bytebin_url
    username = bytebin_username
    password = bytebin_password

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
        auth = aiohttp.BasicAuth(username, password)
        headers = {"Content-Type": "text/html", "Content-Encoding": "gzip"}

        async with session.post(url + "/post", data=compressed_content, headers=headers, auth=auth) as response:
            if response.status == 201:
                response_data = await response.json()
                if "key" in response_data:
                    return f"{bytebin_url}/{response_data['key']}"
                else:
                    print("Unexpected response format:", response_data)
                    return None
            else:
                print(f"Request failed with status {response.status}: {await response.text()}")
                return None
