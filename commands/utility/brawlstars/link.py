from typing import Any

import aiohttp

from api import add_brawlstars_linked_account, get_brawlstars_linked_account
from config import brawlstarsToken
from localizer import tanjunLocalizer
from utility import commandInfo, tanjunEmbed


async def getPlayerInfo(playerTag: str) -> dict[str, str] | None:
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            json_data: Any = await response.json()
            if isinstance(json_data, dict):
                return json_data
            else:
                return None


async def link(commandInfo: commandInfo, playerTag: str) -> None:
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.notFound.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.notFound.description",
                ),
            )
        )
        return

    if await get_brawlstars_linked_account(commandInfo.user.id):
        await commandInfo.reply(
            embed=tanjunEmbed(
                title=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.title",
                ),
                description=tanjunLocalizer.localize(
                    commandInfo.locale,
                    "commands.utility.brawlstars.link.error.alreadyLinked.description",
                ),
            )
        )
        return

    await add_brawlstars_linked_account(commandInfo.user.id, playerTag)

    await commandInfo.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.description",
                tag=playerTag,
            ),
        )
    )
    return
