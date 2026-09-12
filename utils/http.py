"""HTTP-related utilities: GIF search, ImgBB upload, bytebin log upload.

Extracted from ``utility.py`` as part of refactoring (issue #1608).
"""

import gzip
import random
from typing import Any

import aiohttp
from aiohttp import ClientTimeout

from config import (
    ImgBBApiKey,
    bytebin_password,
    bytebin_url,
    bytebin_username,
    giphyAPIKey,
)


async def getGif(query: str, amount: int = 1, limit: int = 10) -> list[str]:  # noqa: N802
    if amount <= 0 or limit <= 0:
        return []
    amount = min(amount, limit)
    limit = min(limit, 50)
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:

            async def fetch(url: str, *, params: dict[str, Any]) -> dict[str, Any] | None:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        return None
                    response_json: dict[str, Any] | None = await response.json()
                    return response_json if isinstance(response_json, dict) else None

            r: dict[str, Any] | None = await fetch(
                "https://api.giphy.com/v1/gifs/search",
                params={"api_key": giphyAPIKey, "q": query, "limit": limit, "rating": "pg"},
            )

            if r is None:
                return []
            results = r.get("data", [])
            if not isinstance(results, list):
                return []
            # nosec: B311
            random.shuffle(results)

            urls: list[str] = []
            for result in results:
                if not isinstance(result, dict):
                    continue
                images = result.get("images")
                medium = images.get("downsized_medium") if isinstance(images, dict) else None
                url = medium.get("url") if isinstance(medium, dict) else None
                if isinstance(url, str) and url:
                    urls.append(url)
                if len(urls) >= amount:
                    break
            return urls
    except (TimeoutError, aiohttp.ClientError):
        return []


async def upload_image_to_imgbb(image_bytes: bytes, file_extension: str) -> dict[str, Any]:
    async with aiohttp.ClientSession(timeout=ClientTimeout(total=30)) as session:
        form_data = aiohttp.FormData()
        form_data.add_field("key", ImgBBApiKey)
        form_data.add_field("image", image_bytes, filename=f"upload.{file_extension}")
        form_data.add_field("name", "tbg")

        async with session.post("https://api.imgbb.com/1/upload", data=form_data) as response:
            if not 200 <= response.status < 300:
                return {}
            response_data = await response.json()

    return response_data if isinstance(response_data, dict) else {}


async def upload_to_tanjun_logs(content: str) -> str | None:
    compressed_content = gzip.compress(content.encode("utf-8"))
    url = bytebin_url
    username = bytebin_username
    password = bytebin_password

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=10)) as session:
        headers = {
            "Authorization": aiohttp.encode_basic_auth(username, password),
            "Content-Type": "text/html",
            "Content-Encoding": "gzip",
        }

        async with session.post(url.rstrip("/") + "/post", data=compressed_content, headers=headers) as response:
            if response.status == 201:
                response_data = await response.json()
                if isinstance(response_data, dict) and isinstance(response_data.get("key"), str):
                    return f"{bytebin_url.rstrip('/')}/{response_data['key']}"
                print("Unexpected response format:", response_data)
                return None
            else:
                print(f"Request failed with status {response.status}: {await response.text()}")
                return None
