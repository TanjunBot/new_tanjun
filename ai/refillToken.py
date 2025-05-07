from datetime import datetime

from discord import Client

from api import resetToken


async def refillAiToken(client: Client):
    now = datetime.now()

    formatted_now = now.strftime("%d %H:%M")

    if formatted_now != "01 00:00":
        return
    skus = await client.fetch_skus()
    plusSku = None
    for sku in skus:
        if sku.name == "Tanjun Plus":
            plusSku = sku

    if plusSku:
        await resetToken(plusSku)
    else:
        await resetToken()
