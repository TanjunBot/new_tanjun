from __future__ import annotations

import json
from pathlib import Path

import aiohttp

from tests.helpers.live_discord.discord_api import DiscordUserClient

ROOT = Path(__file__).resolve().parents[3]
FIXTURE_PATH = ROOT / "tests" / "fixtures" / "e2e" / "test.png"

_MINIMAL_PNG = bytes(
    [
        0x89,
        0x50,
        0x4E,
        0x47,
        0x0D,
        0x0A,
        0x1A,
        0x0A,
        0x00,
        0x00,
        0x00,
        0x0D,
        0x49,
        0x48,
        0x44,
        0x52,
        0x00,
        0x00,
        0x00,
        0x01,
        0x00,
        0x00,
        0x00,
        0x01,
        0x08,
        0x06,
        0x00,
        0x00,
        0x00,
        0x1F,
        0x15,
        0xC4,
        0x89,
        0x00,
        0x00,
        0x00,
        0x0A,
        0x49,
        0x44,
        0x41,
        0x54,
        0x78,
        0x9C,
        0x63,
        0x00,
        0x01,
        0x00,
        0x00,
        0x05,
        0x00,
        0x01,
        0x0D,
        0x0A,
        0x2D,
        0xB4,
        0x00,
        0x00,
        0x00,
        0x00,
        0x49,
        0x45,
        0x4E,
        0x44,
        0xAE,
        0x42,
        0x60,
        0x82,
    ]
)


def ensure_fixture_image() -> Path:
    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_PATH.is_file():
        FIXTURE_PATH.write_bytes(_MINIMAL_PNG)
    return FIXTURE_PATH


async def upload_channel_attachment(
    user_client: DiscordUserClient,
    *,
    channel_id: str,
    filename: str = "test.png",
) -> str:
    path = ensure_fixture_image()
    data = path.read_bytes()
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    form = aiohttp.FormData()
    form.add_field(
        "payload_json",
        json.dumps({"content": "e2e fixture"}),
        content_type="application/json",
    )
    form.add_field(
        "files[0]",
        data,
        filename=filename,
        content_type="image/png",
    )
    headers = {"Authorization": user_client._token}
    async with (
        aiohttp.ClientSession() as session,
        session.post(url, headers=headers, data=form) as resp,
    ):
        body = await resp.json(content_type=None)
        if resp.status not in (200, 201):
            raise RuntimeError(f"Attachment upload failed ({resp.status}): {body}")
        attachments = body.get("attachments") or []
        if not attachments:
            raise RuntimeError(f"Attachment upload returned no attachments: {body}")
        return str(attachments[0]["id"])
