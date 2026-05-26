from datetime import datetime

from discord import Client

from api import resetToken


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
        await resetToken(plus_sku)  # type: ignore[arg-type]
    else:
        await resetToken()
