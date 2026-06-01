from datetime import datetime

from discord import Client

from services.ai_service import AiService


async def refill_ai_token(client: Client) -> None:
    now = datetime.now()

    formatted_now = now.strftime("%d %H:%M")

    if formatted_now != "01 00:00":
        return
    skus = await client.fetch_skus()
    plus_sku = None
    for sku in skus:
        if sku.name == "Tanjun Plus":
            plus_sku = sku

    if plus_sku:
        entitlements = [e async for e in client.entitlements(skus=[plus_sku])]
        await AiService.refill(entitlements)
    else:
        await AiService.refill()
