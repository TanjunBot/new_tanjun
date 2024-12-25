from config import brawlstarsToken
import aiohttp
from utility import commandInfo, tanjunEmbed
from localizer import tanjunLocalizer
from api import get_brawlstars_linked_account, add_brawlstars_linked_account


async def getPlayerInfo(playerTag: str):
    headers = {"Authorization": f"Bearer {brawlstarsToken}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.brawlstars.com/v1/players/%23{playerTag[1:]}",
            headers=headers,
        ) as response:
            if response.status != 200:
                return None
            return await response.json()


async def link(commandInfo: commandInfo, playerTag: str):
    if not playerTag.startswith("#"):
        playerTag = f"#{playerTag}"
    playerInfo = await getPlayerInfo(playerTag)
    if not playerInfo:
        return await commandInfo.reply(
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

    if await get_brawlstars_linked_account(commandInfo.author.id):
        return await commandInfo.reply(
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

    await add_brawlstars_linked_account(commandInfo.author.id, playerTag)

    return await commandInfo.reply(
        embed=tanjunEmbed(
            title=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.title",
            ),
            description=tanjunLocalizer.localize(
                commandInfo.locale,
                "commands.utility.brawlstars.link.success.description",
            ),
        )
    )
